from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from app.db import Base, engine, get_db
from app.routers import cameras, events, layouts, settings as settings_router, video
from app.security import verify_admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version=settings.api_version)
app.include_router(cameras.router)
app.include_router(layouts.router)
app.include_router(events.router)
app.include_router(settings_router.router)
app.include_router(video.router)

Path("app/static").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/api/health", response_model=schemas.HealthOut)
def health(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "api_version": settings.api_version,
        "video_service_status": crud.get_setting(db, "video_service_state", "unknown"),
    }


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    layouts_list = crud.list_layouts(db)
    active_layout = next((l for l in layouts_list if l.is_active), None)
    context = {
        "request": request,
        "active_layout": active_layout,
        "camera_count": len(crud.list_cameras(db)),
        "stream_status": crud.list_stream_status(db),
        "video_status": crud.get_setting(db, "video_service_state", "unknown"),
    }
    return templates.TemplateResponse("dashboard.html", context)


@app.get("/cameras", response_class=HTMLResponse)
def cameras_page(request: Request, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    return templates.TemplateResponse(
        "cameras.html",
        {"request": request, "cameras": crud.list_cameras(db)},
    )


@app.post("/cameras")
def add_camera(
    name: str = Form(...),
    ip_address: str = Form(""),
    rtsp_main_url: str = Form(""),
    rtsp_sub_url: str = Form(""),
    username: str = Form(""),
    password: str = Form(""),
    preferred_stream: str = Form("sub"),
    enabled: bool = Form(False),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
):
    payload = schemas.CameraCreate(
        name=name,
        ip_address=ip_address or None,
        rtsp_main_url=rtsp_main_url or None,
        rtsp_sub_url=rtsp_sub_url or None,
        username=username or None,
        password=password or None,
        preferred_stream=preferred_stream,
        enabled=enabled,
    )
    crud.create_camera(db, payload)
    return RedirectResponse(url="/cameras", status_code=303)


@app.post("/cameras/{camera_id}/delete")
def delete_camera(camera_id: int, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    camera = crud.get_camera(db, camera_id)
    if camera:
        crud.delete_camera(db, camera)
    return RedirectResponse(url="/cameras", status_code=303)


@app.post("/cameras/{camera_id}/update")
def update_camera_ui(
    camera_id: int,
    name: str = Form(...),
    rtsp_main_url: str = Form(""),
    rtsp_sub_url: str = Form(""),
    preferred_stream: str = Form("sub"),
    enabled: bool = Form(False),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
):
    camera = crud.get_camera(db, camera_id)
    if camera:
        crud.update_camera(
            db,
            camera,
            schemas.CameraUpdate(
                name=name,
                rtsp_main_url=rtsp_main_url or None,
                rtsp_sub_url=rtsp_sub_url or None,
                preferred_stream=preferred_stream,
                enabled=enabled,
            ),
        )
    return RedirectResponse(url="/cameras", status_code=303)


@app.post("/cameras/{camera_id}/test")
def test_camera_ui(camera_id: int, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    camera = crud.get_camera(db, camera_id)
    if camera:
        url = camera.rtsp_main_url or camera.rtsp_sub_url
        ok = bool(url and url.startswith("rtsp://"))
        msg = "RTSP URL looks valid" if ok else "Invalid RTSP URL"
        crud.add_event(db, "info" if ok else "error", "camera_test", msg, camera.id)
    return RedirectResponse(url="/cameras", status_code=303)


@app.get("/layouts", response_class=HTMLResponse)
def layouts_page(request: Request, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    return templates.TemplateResponse(
        "layouts.html",
        {
            "request": request,
            "layouts": crud.list_layouts(db),
            "cameras": crud.list_cameras(db),
        },
    )


@app.post("/layouts")
def add_layout(name: str = Form(...), grid_size: int = Form(...), db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    crud.create_layout(db, schemas.LayoutCreate(name=name, grid_size=grid_size))
    return RedirectResponse(url="/layouts", status_code=303)


@app.post("/layouts/{layout_id}/activate")
def activate_layout(layout_id: int, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    crud.activate_layout(db, layout_id)
    return RedirectResponse(url="/layouts", status_code=303)


@app.post("/layouts/{layout_id}/cells/{cell_index}")
def set_cell(
    layout_id: int,
    cell_index: int,
    camera_id: int = Form(0),
    stream_type: str = Form("sub"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
):
    crud.assign_layout_cell(
        db,
        layout_id,
        cell_index,
        schemas.LayoutCellAssign(
            camera_id=camera_id or None,
            stream_type=stream_type,
        ),
    )
    return RedirectResponse(url="/layouts", status_code=303)


@app.get("/status", response_class=HTMLResponse)
def status_page(request: Request, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    cameras_map = {c.id: c for c in crud.list_cameras(db)}
    return templates.TemplateResponse(
        "status.html",
        {"request": request, "statuses": crud.list_stream_status(db), "cameras": cameras_map},
    )


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    return templates.TemplateResponse(
        "settings.html",
        {"request": request, "settings": crud.list_settings(db)},
    )


@app.post("/settings")
def save_settings(
    device_name: str = Form("smartbox"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
):
    crud.upsert_settings(db, {"device_name": device_name})
    return RedirectResponse(url="/settings", status_code=303)


@app.post("/video/reload")
def reload_video_ui(db: Session = Depends(get_db), _: str = Depends(verify_admin)):
    crud.set_setting(db, "video_reload_requested", "1")
    db.commit()
    return RedirectResponse(url="/status", status_code=303)
