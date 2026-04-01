from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.site import CoreFeatureCreate, CoreFeatureUpdate, CoreFeatureOut
from app.crud.crud_site import get_core_features, get_core_feature, create_core_feature, update_core_feature, soft_delete_core_feature
from app.models.user import User

router = APIRouter(prefix="/core-features", tags=["Core Features"])


@router.get("/", response_model=List[CoreFeatureOut])
def list_features(db: Session = Depends(get_db)):
    return get_core_features(db)


@router.get("/{feature_id}", response_model=CoreFeatureOut)
def get_one(feature_id: int, db: Session = Depends(get_db)):
    obj = get_core_feature(db, feature_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Core feature not found")
    return obj


@router.post("/", response_model=CoreFeatureOut, status_code=201)
def create(data: CoreFeatureCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return create_core_feature(db, data)


@router.put("/{feature_id}", response_model=CoreFeatureOut)
def update(feature_id: int, data: CoreFeatureUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_core_feature(db, feature_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Core feature not found")
    return obj


@router.delete("/{feature_id}", status_code=204)
def delete(feature_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_core_feature(db, feature_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Core feature not found")
    soft_delete_core_feature(db, feature_id, deleted_by=current_user.id)
