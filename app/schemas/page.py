from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# ─── Page ────────────────────────────────────────────────────────
class PageCreate(BaseModel):
    title: str
    slug: str
    content: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class PageUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class PageSectionCreate(BaseModel):
    section_type: str
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    display_order: Optional[int] = 0


class PageSectionUpdate(BaseModel):
    section_type: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    display_order: Optional[int] = None


class PageSectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    page_id: int
    section_type: str
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int = 0


class PageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: Optional[int] = None
    title: str
    slug: str
    content: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    updated_at: Optional[datetime] = None

    sections: List[PageSectionOut] = []


# ─── Faq ─────────────────────────────────────────────────────────
class FaqCreate(BaseModel):
    question: str
    answer: str
    display_order: Optional[int] = None
    is_active: Optional[bool] = True


class FaqUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class FaqOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    answer: str
    display_order: Optional[int] = None
    is_active: bool
