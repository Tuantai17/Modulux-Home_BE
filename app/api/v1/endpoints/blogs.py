import math

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.blog_sync_repository import BlogSyncRepository
from app.schemas.blog_sync import BlogDetailOut, BlogListItem, BlogPaginationOut

router = APIRouter(prefix="/blogs", tags=["Blogs"])


def _extract_image_url(content: str) -> str | None:
    soup = BeautifulSoup(content or "", "html.parser")
    image = soup.find("img")
    return image.get("src") if image else None


def _extract_excerpt(content: str, *, limit: int = 180) -> str:
    soup = BeautifulSoup(content or "", "html.parser")
    cover = soup.find("figure", attrs={"data-blog-cover": "true"})
    if cover:
        cover.decompose()
    text = " ".join(soup.get_text(" ", strip=True).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _to_blog_list_item(blog) -> BlogListItem:
    excerpt = _extract_excerpt(blog.content)
    return BlogListItem(
        id=blog.id,
        title=blog.title,
        type=blog.blog_type,
        source_type=blog.source_type,
        type_override=blog.type_override,
        is_type_overridden=bool(blog.type_override),
        slug=blog.slug,
        source_url=blog.source_url,
        excerpt=excerpt,
        image_url=_extract_image_url(blog.content),
        created_at=blog.created_at,
        updated_at=blog.updated_at,
        last_synced_at=blog.last_synced_at,
    )


@router.get("/", response_model=BlogPaginationOut)
def list_blogs(
    page: int = Query(1, ge=1),
    page_size: int = Query(9, ge=1, le=50),
    db: Session = Depends(get_db),
):
    repository = BlogSyncRepository()
    blogs, total = repository.list_blogs(db, page=page, page_size=page_size)
    items = [_to_blog_list_item(blog) for blog in blogs]
    total_pages = math.ceil(total / page_size) if total else 0

    return BlogPaginationOut(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{slug}", response_model=BlogDetailOut)
def get_blog_detail(slug: str, db: Session = Depends(get_db)):
    repository = BlogSyncRepository()
    blog = repository.get_blog_by_slug(db, slug)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    summary = _to_blog_list_item(blog)
    return BlogDetailOut(**summary.model_dump(), content=blog.content)
