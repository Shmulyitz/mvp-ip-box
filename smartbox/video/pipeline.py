from collections.abc import Iterable
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from app.models import Camera, Layout, LayoutCell
from app.security import decrypt_secret
from video.gst_utils import pick_decoder
from video.layout import compute_grid


@dataclass
class PipelinePlan:
    launch: str
    camera_ids: list[int]


def _safe_rtsp_url(camera: Camera, requested: str, grid_size: int) -> str | None:
    if grid_size == 16:
        requested = "sub"
    if grid_size == 1 and camera.rtsp_main_url:
        requested = "main"
    if requested == "main":
        return camera.rtsp_main_url or camera.rtsp_sub_url
    return camera.rtsp_sub_url or camera.rtsp_main_url


def _placeholder_source(sink_idx: int, width: int, height: int, label: str) -> str:
    txt = label.replace('"', "")
    return (
        f"videotestsrc is-live=true pattern=black ! "
        f"video/x-raw,width={width},height={height},framerate=15/1 ! "
        f"textoverlay text=\"{txt}\" valignment=center halignment=center font-desc=\"Sans 24\" ! "
        f"queue ! comp.sink_{sink_idx}"
    )


def _camera_source(sink_idx: int, width: int, height: int, url: str) -> str:
    decoder = pick_decoder()
    return (
        f"rtspsrc location=\"{url}\" protocols=tcp latency=500 timeout=5000000 ! "
        f"rtph264depay ! h264parse ! {decoder} ! videoconvert ! videoscale ! "
        f"video/x-raw,width={width},height={height},framerate=15/1 ! "
        f"queue max-size-buffers=0 max-size-bytes=0 max-size-time=0 ! comp.sink_{sink_idx}"
    )


def build_pipeline(layout: Layout, cells: Iterable[LayoutCell], camera_map: dict[int, Camera], failed_cameras: set[int]) -> PipelinePlan:
    geometries = {g.cell_index: g for g in compute_grid(layout.grid_size)}
    sink_props: list[str] = []
    source_parts: list[str] = []
    camera_ids: list[int] = []

    for cell in sorted(cells, key=lambda c: c.cell_index):
        if cell.cell_index not in geometries:
            continue
        geo = geometries[cell.cell_index]
        sink_props.append(
            f"sink_{cell.cell_index}::xpos={geo.x} sink_{cell.cell_index}::ypos={geo.y} "
            f"sink_{cell.cell_index}::width={geo.width} sink_{cell.cell_index}::height={geo.height}"
        )

        camera = camera_map.get(cell.camera_id) if cell.camera_id else None
        if not camera or not camera.enabled:
            source_parts.append(_placeholder_source(cell.cell_index, geo.width, geo.height, "EMPTY"))
            continue

        url = _safe_rtsp_url(camera, cell.stream_type or camera.preferred_stream, layout.grid_size)
        if not url:
            source_parts.append(_placeholder_source(cell.cell_index, geo.width, geo.height, "NO URL"))
            continue

        if camera.id in failed_cameras:
            source_parts.append(_placeholder_source(cell.cell_index, geo.width, geo.height, "OFFLINE"))
            continue

        password = decrypt_secret(camera.password_encrypted)
        if camera.username and password:
            parsed = urlsplit(url)
            if parsed.scheme == "rtsp" and "@" not in parsed.netloc:
                netloc = f"{camera.username}:{password}@{parsed.netloc}"
                url = urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))

        source_parts.append(_camera_source(cell.cell_index, geo.width, geo.height, url))
        camera_ids.append(camera.id)

    if not source_parts:
        source_parts.append(_placeholder_source(0, 1920, 1080, "NO SOURCES"))
        sink_props.append("sink_0::xpos=0 sink_0::ypos=0 sink_0::width=1920 sink_0::height=1080")

    launch = (
        f"compositor name=comp background=black {' '.join(sink_props)} ! "
        "videoconvert ! video/x-raw,width=1920,height=1080,framerate=15/1 ! autovideosink sync=false "
        + " ".join(source_parts)
    )
    return PipelinePlan(launch=launch, camera_ids=camera_ids)
