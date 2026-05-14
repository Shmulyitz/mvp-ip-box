from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db
from app.security import verify_admin

router = APIRouter(prefix="/api/events", tags=["events"], dependencies=[Depends(verify_admin)])


@router.get("", response_model=list[schemas.EventOut])
def list_all(db: Session = Depends(get_db)):
    return crud.list_events(db)
