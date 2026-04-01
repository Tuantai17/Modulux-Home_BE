from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ─── Category ────────────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str
    slug: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


# ─── Post ────────────────────────────────────────────────────────
class PostCreate(BaseModel):
    category_id: Optional[int] = None
    title: str
    slug: str
    thumbnail_url: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    published_at: Optional[datetime] = None


class PostUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    thumbnail_url: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    published_at: Optional[datetime] = None


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: Optional[int] = None
    author_id: Optional[int] = None
    title: str
    slug: str
    thumbnail_url: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
