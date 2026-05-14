import os
import signal
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.db import get_db
from app.security import verify_admin

router = APIRouter(prefix="/api/video", tags=["video"], dependencies=[Depends(verify_admin)])


def _read_pid() -> int | None:
    pid_file = Path("/run/smartbox-video.pid")
    if not pid_file.exists():
        return None
    try:
        return int(pid_file.read_text().strip())
    except Exception:
        return None


@router.post("/reload")
def reload_video(db: Session = Depends(get_db)):
    crud.set_setting(db, "video_reload_requested", "1")
    db.commit()
    pid = _read_pid()
    if pid:
        try:
            os.kill(pid, signal.SIGUSR1)
        except Exception:
            pass
    return {"reloaded": True}


@router.post("/restart")
def restart_video(db: Session = Depends(get_db)):
    crud.set_setting(db, "video_reload_requested", "1")
    db.commit()
    return {"restart_requested": True}


@router.get("/status")
def video_status(db: Session = Depends(get_db)):
    statuses = crud.list_stream_status(db)
    return {
        "service": crud.get_setting(db, "video_service_state", "unknown"),
        "streams": statuses,
    }
