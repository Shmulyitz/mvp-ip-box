from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db
from app.security import verify_admin

router = APIRouter(prefix="/api/cameras", tags=["cameras"], dependencies=[Depends(verify_admin)])


def _to_camera_out(camera):
    return schemas.CameraOut(
        id=camera.id,
        name=camera.name,
        ip_address=camera.ip_address,
        rtsp_main_url=camera.rtsp_main_url,
        rtsp_sub_url=camera.rtsp_sub_url,
        username=camera.username,
        password="***",
        preferred_stream=camera.preferred_stream,
        enabled=camera.enabled,
        created_at=camera.created_at,
        updated_at=camera.updated_at,
    )


@router.get("", response_model=list[schemas.CameraOut])
def list_all(db: Session = Depends(get_db)):
    cameras = crud.list_cameras(db)
    return [_to_camera_out(c) for c in cameras]


@router.post("", response_model=schemas.CameraOut)
def create(payload: schemas.CameraCreate, db: Session = Depends(get_db)):
    camera = crud.create_camera(db, payload)
    return _to_camera_out(camera)


@router.get("/{camera_id}", response_model=schemas.CameraOut)
def get(camera_id: int, db: Session = Depends(get_db)):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return _to_camera_out(camera)


@router.put("/{camera_id}", response_model=schemas.CameraOut)
def update(camera_id: int, payload: schemas.CameraUpdate, db: Session = Depends(get_db)):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera = crud.update_camera(db, camera, payload)
    return _to_camera_out(camera)


@router.delete("/{camera_id}")
def remove(camera_id: int, db: Session = Depends(get_db)):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    crud.delete_camera(db, camera)
    return {"deleted": True}


@router.post("/{camera_id}/test")
def test(camera_id: int, db: Session = Depends(get_db)):
    camera = crud.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    url = camera.rtsp_main_url or camera.rtsp_sub_url
    ok = bool(url and url.startswith("rtsp://"))
    msg = "RTSP URL looks valid" if ok else "Invalid RTSP URL"
    crud.add_event(db, "info" if ok else "error", "camera_test", msg, camera.id)
    return {"ok": ok, "message": msg}
