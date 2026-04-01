from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.site import BannerCreate, BannerUpdate, BannerOut
from app.crud.crud_site import get_banners, get_banner, create_banner, update_banner, soft_delete_banner
from app.models.user import User

router = APIRouter(prefix="/banners", tags=["Banners"])


@router.get("/", response_model=List[BannerOut])
def list_banners(db: Session = Depends(get_db)):
    return get_banners(db)


@router.get("/{banner_id}", response_model=BannerOut)
def get_one(banner_id: int, db: Session = Depends(get_db)):
    obj = get_banner(db, banner_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Banner not found")
    return obj


@router.post("/", response_model=BannerOut, status_code=201)
def create(data: BannerCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return create_banner(db, data)


@router.put("/{banner_id}", response_model=BannerOut)
def update(banner_id: int, data: BannerUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_banner(db, banner_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Banner not found")
    return obj


@router.delete("/{banner_id}", status_code=204)
def delete(banner_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_banner(db, banner_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Banner not found")
    soft_delete_banner(db, banner_id, deleted_by=current_user.id)
