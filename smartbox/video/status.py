from sqlalchemy.orm import Session

from app import crud


def set_video_state(db: Session, state: str):
    crud.set_setting(db, "video_service_state", state)
    db.commit()


def mark_reload_handled(db: Session):
    crud.set_setting(db, "video_reload_requested", "0")
    db.commit()


def request_reload(db: Session):
    crud.set_setting(db, "video_reload_requested", "1")
    db.commit()
