from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db
from app.security import verify_admin

router = APIRouter(prefix="/api/settings", tags=["settings"], dependencies=[Depends(verify_admin)])


class SettingsUpdate(BaseModel):
    values: dict[str, str]


@router.get("", response_model=list[schemas.SettingOut])
def get_settings(db: Session = Depends(get_db)):
    return crud.list_settings(db)


@router.put("", response_model=list[schemas.SettingOut])
def put_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    return crud.upsert_settings(db, payload.values)
