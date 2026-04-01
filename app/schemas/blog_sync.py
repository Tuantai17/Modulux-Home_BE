from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BlogListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    type: str
    source_type: str
    type_override: str | None = None
    is_type_overridden: bool = False
    slug: str
    source_url: str
    excerpt: str
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime
    last_synced_at: datetime


class BlogDetailOut(BlogListItem):
    content: str


class BlogPaginationOut(BaseModel):
    items: list[BlogListItem]
    page: int
    page_size: int
    total: int
    total_pages: int


class SyncLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    total: int
    inserted: int
    updated: int
    skipped: int
    created_at: datetime


class SyncStartedOut(BaseModel):
    message: str
    started_at: datetime


class SyncSummaryOut(BaseModel):
    total: int
    inserted: int
    updated: int
    skipped: int


class ImportUrlIn(BaseModel):
    url: str


class BlogTypeUpdateIn(BaseModel):
    type: str | None = None


class BlogTypeUpdateOut(BaseModel):
    id: int
    type: str
    source_type: str
    type_override: str | None = None
    is_type_overridden: bool
