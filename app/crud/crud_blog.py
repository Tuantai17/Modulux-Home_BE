from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.blog import Category, Post
from app.schemas.blog import CategoryCreate, CategoryUpdate, PostCreate, PostUpdate

_now = lambda: datetime.now(timezone.utc)


# ─── Category ────────────────────────────────────────────────────
def get_categories(db: Session):
    return db.query(Category).filter(Category.delete_at == None).all()


def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id, Category.delete_at == None).first()


def get_category_by_slug(db: Session, slug: str):
    return db.query(Category).filter(Category.slug == slug, Category.delete_at == None).first()


def create_category(db: Session, data: CategoryCreate):
    obj = Category(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_category(db: Session, category_id: int, data: CategoryUpdate):
    obj = get_category(db, category_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_category(db: Session, category_id: int, deleted_by: int):
    obj = get_category(db, category_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj


# ─── Post ────────────────────────────────────────────────────────
def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Post).filter(Post.delete_at == None).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id, Post.delete_at == None).first()


def get_post_by_slug(db: Session, slug: str):
    return db.query(Post).filter(Post.slug == slug, Post.delete_at == None).first()


def create_post(db: Session, data: PostCreate, author_id: int):
    obj = Post(**data.model_dump(), author_id=author_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_post(db: Session, post_id: int, data: PostUpdate):
    obj = get_post(db, post_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_post(db: Session, post_id: int, deleted_by: int):
    obj = get_post(db, post_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj
