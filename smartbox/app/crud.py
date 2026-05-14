from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.security import encrypt_secret

VALID_GRIDS = {1, 4, 9, 16}


def create_camera(db: Session, camera: schemas.CameraCreate) -> models.Camera:
    db_camera = models.Camera(
        name=camera.name,
        ip_address=camera.ip_address,
        rtsp_main_url=camera.rtsp_main_url,
        rtsp_sub_url=camera.rtsp_sub_url,
        username=camera.username,
        password_encrypted=encrypt_secret(camera.password),
        preferred_stream=camera.preferred_stream,
        enabled=camera.enabled,
    )
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


def list_cameras(db: Session) -> list[models.Camera]:
    return db.execute(select(models.Camera).order_by(models.Camera.id)).scalars().all()


def get_camera(db: Session, camera_id: int) -> models.Camera | None:
    return db.get(models.Camera, camera_id)


def update_camera(db: Session, camera: models.Camera, payload: schemas.CameraUpdate) -> models.Camera:
    data = payload.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    for key, value in data.items():
        setattr(camera, key, value)
    if password is not None:
        camera.password_encrypted = encrypt_secret(password)
    camera.updated_at = datetime.utcnow()
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def delete_camera(db: Session, camera: models.Camera) -> None:
    db.delete(camera)
    db.commit()


def create_layout(db: Session, payload: schemas.LayoutCreate) -> models.Layout:
    if payload.grid_size not in VALID_GRIDS:
        raise ValueError("grid_size must be one of 1, 4, 9, 16")
    layout = models.Layout(name=payload.name, grid_size=payload.grid_size)
    db.add(layout)
    db.flush()
    for i in range(payload.grid_size):
        db.add(models.LayoutCell(layout_id=layout.id, cell_index=i, stream_type="sub"))
    db.commit()
    return get_layout(db, layout.id)


def list_layouts(db: Session) -> list[models.Layout]:
    stmt = select(models.Layout).options(joinedload(models.Layout.cells)).order_by(models.Layout.id)
    return db.execute(stmt).unique().scalars().all()


def get_layout(db: Session, layout_id: int) -> models.Layout | None:
    stmt = select(models.Layout).options(joinedload(models.Layout.cells)).where(models.Layout.id == layout_id)
    return db.execute(stmt).unique().scalars().first()


def update_layout(db: Session, layout: models.Layout, payload: schemas.LayoutUpdate) -> models.Layout:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(layout, key, value)
    if "grid_size" in data and layout.grid_size in VALID_GRIDS:
        db.execute(delete(models.LayoutCell).where(models.LayoutCell.layout_id == layout.id))
        for i in range(layout.grid_size):
            db.add(models.LayoutCell(layout_id=layout.id, cell_index=i, stream_type="sub"))
    layout.updated_at = datetime.utcnow()
    db.add(layout)
    db.commit()
    return get_layout(db, layout.id)


def delete_layout(db: Session, layout: models.Layout) -> None:
    db.delete(layout)
    db.commit()


def activate_layout(db: Session, layout_id: int) -> models.Layout | None:
    db.query(models.Layout).update({models.Layout.is_active: False})
    layout = db.get(models.Layout, layout_id)
    if layout is None:
        db.rollback()
        return None
    layout.is_active = True
    layout.updated_at = datetime.utcnow()
    db.add(layout)
    set_setting(db, "video_reload_requested", "1")
    db.commit()
    return get_layout(db, layout_id)


def assign_layout_cell(db: Session, layout_id: int, cell_index: int, payload: schemas.LayoutCellAssign) -> models.LayoutCell | None:
    cell = db.execute(
        select(models.LayoutCell).where(
            models.LayoutCell.layout_id == layout_id,
            models.LayoutCell.cell_index == cell_index,
        )
    ).scalar_one_or_none()
    if cell is None:
        return None
    cell.camera_id = payload.camera_id
    cell.stream_type = payload.stream_type
    db.add(cell)
    set_setting(db, "video_reload_requested", "1")
    db.commit()
    db.refresh(cell)
    return cell


def list_events(db: Session, limit: int = 200) -> list[models.Event]:
    stmt = select(models.Event).order_by(models.Event.created_at.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


def add_event(db: Session, level: str, event_type: str, message: str, camera_id: int | None = None):
    ev = models.Event(level=level, event_type=event_type, message=message, camera_id=camera_id)
    db.add(ev)
    db.commit()
    return ev


def set_setting(db: Session, key: str, value: str):
    setting = db.get(models.Setting, key)
    if setting is None:
        setting = models.Setting(key=key, value=value)
    else:
        setting.value = value
    db.add(setting)
    db.flush()
    return setting


def get_setting(db: Session, key: str, default: str = "") -> str:
    setting = db.get(models.Setting, key)
    return setting.value if setting else default


def list_settings(db: Session) -> list[models.Setting]:
    return db.execute(select(models.Setting).order_by(models.Setting.key)).scalars().all()


def upsert_settings(db: Session, items: dict[str, str]) -> list[models.Setting]:
    for key, value in items.items():
        set_setting(db, key, value)
    db.commit()
    return list_settings(db)


def upsert_stream_status(
    db: Session,
    camera_id: int,
    status: str,
    last_error: str | None = None,
    increment_reconnect: bool = False,
    fps: float | None = None,
):
    row = db.get(models.StreamStatus, camera_id)
    if row is None:
        row = models.StreamStatus(camera_id=camera_id, reconnect_count=0)
    row.status = status
    row.updated_at = datetime.utcnow()
    row.last_frame_at = datetime.utcnow() if status == "online" else row.last_frame_at
    row.last_error = last_error
    row.fps = fps if fps is not None else row.fps
    if increment_reconnect:
        row.reconnect_count += 1
    db.add(row)
    db.commit()
    return row


def list_stream_status(db: Session) -> list[models.StreamStatus]:
    return db.execute(select(models.StreamStatus).order_by(models.StreamStatus.camera_id)).scalars().all()
