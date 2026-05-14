from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import get_db
from app.security import verify_admin

router = APIRouter(prefix="/api/layouts", tags=["layouts"], dependencies=[Depends(verify_admin)])


@router.get("", response_model=list[schemas.LayoutOut])
def list_all(db: Session = Depends(get_db)):
    return crud.list_layouts(db)


@router.post("", response_model=schemas.LayoutOut)
def create(payload: schemas.LayoutCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_layout(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{layout_id}", response_model=schemas.LayoutOut)
def get(layout_id: int, db: Session = Depends(get_db)):
    layout = crud.get_layout(db, layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    return layout


@router.put("/{layout_id}", response_model=schemas.LayoutOut)
def update(layout_id: int, payload: schemas.LayoutUpdate, db: Session = Depends(get_db)):
    layout = crud.get_layout(db, layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    return crud.update_layout(db, layout, payload)


@router.delete("/{layout_id}")
def remove(layout_id: int, db: Session = Depends(get_db)):
    layout = crud.get_layout(db, layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    crud.delete_layout(db, layout)
    return {"deleted": True}


@router.post("/{layout_id}/activate", response_model=schemas.LayoutOut)
def activate(layout_id: int, db: Session = Depends(get_db)):
    layout = crud.activate_layout(db, layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    crud.add_event(db, "info", "layout", f"Activated layout {layout.name}")
    return layout


@router.put("/{layout_id}/cells/{cell_index}", response_model=schemas.LayoutCellOut)
def assign(layout_id: int, cell_index: int, payload: schemas.LayoutCellAssign, db: Session = Depends(get_db)):
    cell = crud.assign_layout_cell(db, layout_id, cell_index, payload)
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    return cell
