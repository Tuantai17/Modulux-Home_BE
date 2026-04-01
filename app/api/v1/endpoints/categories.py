from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.blog import CategoryCreate, CategoryUpdate, CategoryOut
from app.crud.crud_blog import get_categories, get_category, get_category_by_slug, create_category, update_category, soft_delete_category
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return get_categories(db)


@router.get("/slug/{slug}", response_model=CategoryOut)
def get_by_slug(slug: str, db: Session = Depends(get_db)):
    obj = get_category_by_slug(db, slug)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return obj


@router.get("/{category_id}", response_model=CategoryOut)
def get_one(category_id: int, db: Session = Depends(get_db)):
    obj = get_category(db, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return obj


@router.post("/", response_model=CategoryOut, status_code=201)
def create(data: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return create_category(db, data)


@router.put("/{category_id}", response_model=CategoryOut)
def update(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_category(db, category_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return obj


@router.delete("/{category_id}", status_code=204)
def delete(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_category(db, category_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Category not found")
    soft_delete_category(db, category_id, deleted_by=current_user.id)
