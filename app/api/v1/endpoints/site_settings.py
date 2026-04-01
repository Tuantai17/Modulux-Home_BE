from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.site import SiteSettingCreate, SiteSettingUpdate, SiteSettingOut
from app.crud.crud_site import get_settings, get_setting, get_setting_by_key, create_setting, update_setting, soft_delete_setting
from app.models.user import User

router = APIRouter(prefix="/site-settings", tags=["Site Settings"])


@router.get("/", response_model=List[SiteSettingOut])
def list_settings(db: Session = Depends(get_db)):
    return get_settings(db)


@router.get("/{setting_id}", response_model=SiteSettingOut)
def get_one(setting_id: int, db: Session = Depends(get_db)):
    obj = get_setting(db, setting_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Setting not found")
    return obj


@router.post("/", response_model=SiteSettingOut, status_code=201)
def create(data: SiteSettingCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return create_setting(db, data)


@router.put("/{setting_id}", response_model=SiteSettingOut)
def update(setting_id: int, data: SiteSettingUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_setting(db, setting_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Setting not found")
    return obj


@router.delete("/{setting_id}", status_code=204)
def delete(setting_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_setting(db, setting_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Setting not found")
    soft_delete_setting(db, setting_id, deleted_by=current_user.id)
