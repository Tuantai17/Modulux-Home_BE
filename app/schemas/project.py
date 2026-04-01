from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── ProjectImage ────────────────────────────────────────────────
class ProjectImageCreate(BaseModel):
    project_id: int
    image_url: str
    display_order: Optional[int] = None
    is_hero: Optional[bool] = False
    is_floor_plan: Optional[bool] = False


class ProjectImageUpdate(BaseModel):
    image_url: Optional[str] = None
    display_order: Optional[int] = None
    is_hero: Optional[bool] = None
    is_floor_plan: Optional[bool] = None


class ProjectImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    image_url: str
    display_order: Optional[int] = None
    is_hero: bool
    is_floor_plan: bool


# ─── Project ─────────────────────────────────────────────────────
class ProjectCreate(BaseModel):
    title: str
    slug: str
    thumbnail_url: Optional[str] = None
    installation_time: Optional[str] = None
    location: Optional[str] = None
    area_sqft: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    stories: Optional[int] = None
    kitchens: Optional[int] = None
    floor_plan_url: Optional[str] = None
    video_url: Optional[str] = None
    features: Optional[List[str]] = None
    finishing_options: Optional[List[str]] = None
    description: Optional[str] = None
    content: Optional[str] = None
    is_featured: Optional[bool] = False
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    thumbnail_url: Optional[str] = None
    installation_time: Optional[str] = None
    location: Optional[str] = None
    area_sqft: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    stories: Optional[int] = None
    kitchens: Optional[int] = None
    floor_plan_url: Optional[str] = None
    video_url: Optional[str] = None
    features: Optional[List[str]] = None
    finishing_options: Optional[List[str]] = None
    description: Optional[str] = None
    content: Optional[str] = None
    is_featured: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: Optional[int] = None
    title: str
    slug: str
    thumbnail_url: Optional[str] = None
    installation_time: Optional[str] = None
    location: Optional[str] = None
    area_sqft: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    stories: Optional[int] = None
    kitchens: Optional[int] = None
    floor_plan_url: Optional[str] = None
    video_url: Optional[str] = None
    features: Optional[List[str]] = None
    finishing_options: Optional[List[str]] = None
    description: Optional[str] = None
    content: Optional[str] = None
    is_featured: bool
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: Optional[datetime] = None
    images: List[ProjectImageOut] = []
