import logging
import os
import signal
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import gi
from sqlalchemy import select

from app import crud, models
from app.db import SessionLocal
from video.gst_utils import get_error_message, init_gst
from video.pipeline import build_pipeline, output_sink
from video.status import mark_reload_handled, set_video_state

gi.require_version("Gst", "1.0")
gi.require_version("GLib", "2.0")
from gi.repository import GLib, Gst


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("smartbox-video")


class VideoEngine:
    def __init__(self):
        self.pipeline: Gst.Pipeline | None = None
        self.loop: GLib.MainLoop | None = None
        self.failed_cameras: set[int] = set()
        self.failed_until: dict[int, float] = {}
        self.current_camera_ids: list[int] = []
        self.rebuild_requested = True
        self.last_layout_id: int | None = None

    def load_active_layout(self):
        with SessionLocal() as db:
            layout = db.execute(select(models.Layout).where(models.Layout.is_active.is_(True))).scalars().first()
            if not layout:
                return None, [], {}
            layout = crud.get_layout(db, layout.id)
            cameras = crud.list_cameras(db)
            camera_map = {c.id: c for c in cameras}
            return layout, layout.cells, camera_map

    def _set_status_connecting(self, camera_ids: list[int]):
        with SessionLocal() as db:
            for camera_id in camera_ids:
                crud.upsert_stream_status(db, camera_id, "connecting")

    def _set_status_online(self, camera_ids: list[int]):
        with SessionLocal() as db:
            for camera_id in camera_ids:
                crud.upsert_stream_status(db, camera_id, "online")

    def _build(self):
        layout, cells, camera_map = self.load_active_layout()
        if not layout:
            logger.info("No active layout found; rendering fallback placeholder")
            launch = f"videotestsrc is-live=true pattern=black ! textoverlay text=\"NO ACTIVE LAYOUT\" valignment=center halignment=center ! {output_sink()}"
            self.current_camera_ids = []
        else:
            now = time.time()
            self.failed_cameras = {cid for cid, until in self.failed_until.items() if until > now}
            plan = build_pipeline(layout, cells, camera_map, self.failed_cameras)
            launch = plan.launch
            self.current_camera_ids = plan.camera_ids
            self.last_layout_id = layout.id
            logger.info("Intended pipeline (%s-grid): %s", layout.grid_size, self._mask_launch(launch))

        if self.pipeline is not None:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None

        self.pipeline = Gst.parse_launch(launch)
        if not self.pipeline:
            raise RuntimeError("Failed to build pipeline")

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_bus_message)

        self._set_status_connecting(self.current_camera_ids)
        self.pipeline.set_state(Gst.State.PLAYING)
        self._set_status_online(self.current_camera_ids)

        with SessionLocal() as db:
            set_video_state(db, "running")
            mark_reload_handled(db)

    def on_bus_message(self, _bus, message):
        if message.type == Gst.MessageType.ERROR:
            detail = get_error_message(message)
            logger.error("Pipeline error: %s", detail)
            with SessionLocal() as db:
                for camera_id in self.current_camera_ids:
                    crud.upsert_stream_status(
                        db,
                        camera_id,
                        "offline",
                        last_error=detail,
                        increment_reconnect=True,
                    )
                    crud.add_event(db, "error", "stream", detail, camera_id=camera_id)
                    self.failed_until[camera_id] = time.time() + 5
            self.rebuild_requested = True

        if message.type == Gst.MessageType.EOS:
            logger.warning("Pipeline EOS received")
            self.rebuild_requested = True

    def poll_reload(self):
        with SessionLocal() as db:
            needs_reload = crud.get_setting(db, "video_reload_requested", "0") == "1"
            if needs_reload:
                logger.info("Reload requested via settings flag")
                self.rebuild_requested = True

        if self.rebuild_requested:
            self.rebuild_requested = False
            try:
                self._build()
            except Exception as exc:
                logger.exception("Failed to build pipeline: %s", exc)
                with SessionLocal() as db:
                    set_video_state(db, "error")
                    crud.add_event(db, "error", "video", f"Pipeline build failed: {exc}")

        return True

    def _mask_launch(self, launch: str) -> str:
        out = launch
        markers = ["location=\"rtsp://", "location=rtsp://"]
        for marker in markers:
            start = 0
            while True:
                idx = out.find(marker, start)
                if idx == -1:
                    break
                value_start = idx + len("location=")
                quote = out[value_start] if out[value_start] in {'"', "'"} else ""
                if quote:
                    value_start += 1
                    end = out.find(quote, value_start)
                else:
                    end = out.find(" ", value_start)
                if end == -1:
                    end = len(out)
                raw = out[value_start:end]
                masked = self._mask_url(raw)
                out = out[:value_start] + masked + out[end:]
                start = value_start + len(masked)
        return out

    @staticmethod
    def _mask_url(url: str) -> str:
        parsed = urlsplit(url)
        if "@" not in parsed.netloc:
            return url
        creds, host = parsed.netloc.split("@", 1)
        if ":" in creds:
            user, _ = creds.split(":", 1)
            netloc = f"{user}:***@{host}"
        else:
            netloc = f"***@{host}"
        return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))

    def run(self):
        init_gst()
        self.loop = GLib.MainLoop()

        pid_file = Path("/run/smartbox-video.pid")
        try:
            pid_file.write_text(str(os.getpid()), encoding="utf-8")
        except Exception:
            pass

        def _signal_reload(signum, _frame):
            if signum in (signal.SIGTERM, signal.SIGINT):
                if self.loop is not None:
                    self.loop.quit()
            else:
                self.rebuild_requested = True

        signal.signal(signal.SIGTERM, _signal_reload)
        signal.signal(signal.SIGINT, _signal_reload)
        signal.signal(signal.SIGUSR1, _signal_reload)

        GLib.timeout_add_seconds(2, self.poll_reload)
        self.poll_reload()

        try:
            self.loop.run()
        finally:
            if self.pipeline is not None:
                self.pipeline.set_state(Gst.State.NULL)
            with SessionLocal() as db:
                set_video_state(db, "stopped")


def main():
    VideoEngine().run()


if __name__ == "__main__":
    main()
