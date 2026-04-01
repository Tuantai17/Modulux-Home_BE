from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.blog import PostCreate, PostUpdate, PostOut
from app.crud.crud_blog import get_posts, get_post, get_post_by_slug, create_post, update_post, soft_delete_post
from app.models.user import User

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[PostOut])
def list_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_posts(db, skip=skip, limit=limit)


@router.get("/slug/{slug}", response_model=PostOut)
def get_by_slug(slug: str, db: Session = Depends(get_db)):
    obj = get_post_by_slug(db, slug)
    if not obj:
        raise HTTPException(status_code=404, detail="Post not found")
    return obj


@router.get("/{post_id}", response_model=PostOut)
def get_one(post_id: int, db: Session = Depends(get_db)):
    obj = get_post(db, post_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Post not found")
    return obj


@router.post("/", response_model=PostOut, status_code=201)
def create(data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_post(db, data, author_id=current_user.id)


@router.put("/{post_id}", response_model=PostOut)
def update(post_id: int, data: PostUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_post(db, post_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Post not found")
    return obj


@router.delete("/{post_id}", status_code=204)
def delete(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_post(db, post_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Post not found")
    soft_delete_post(db, post_id, deleted_by=current_user.id)
