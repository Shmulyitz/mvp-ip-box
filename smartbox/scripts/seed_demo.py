from sqlalchemy import select

from app import crud, models, schemas
from app.db import SessionLocal


def main():
    with SessionLocal() as db:
        if not db.execute(select(models.Camera)).scalars().first():
            crud.create_camera(
                db,
                schemas.CameraCreate(
                    name="Demo Camera",
                    ip_address="192.168.1.10",
                    rtsp_main_url="rtsp://192.168.1.10/main",
                    rtsp_sub_url="rtsp://192.168.1.10/sub",
                    preferred_stream="sub",
                    enabled=True,
                ),
            )
        if not db.execute(select(models.Layout)).scalars().first():
            layout = crud.create_layout(db, schemas.LayoutCreate(name="Default 4-grid", grid_size=4))
            crud.activate_layout(db, layout.id)
    print("Seed data created")


if __name__ == "__main__":
    main()
