from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.blog_sync import Blog
from app.models.project import Project
from app.schemas.search import SearchResponseOut, SearchResultOut

router = APIRouter(prefix="/search", tags=["Search"])


def _collapse_text(value: str | None, *, limit: int = 150) -> str:
    soup = BeautifulSoup(value or "", "html.parser")
    text = " ".join(soup.get_text(" ", strip=True).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _normalize_query(value: str) -> str:
    return " ".join((value or "").split()).strip()


def _score_text(value: str | None, query: str) -> float:
    haystack = (value or "").lower()
    needle = query.lower()
    if not haystack or not needle:
        return 0.0
    if haystack == needle:
        return 10.0
    if haystack.startswith(needle):
        return 7.0
    if needle in haystack:
        return 4.0
    return 0.0


def _project_result(project: Project) -> SearchResultOut:
    excerpt = _collapse_text(project.description or project.content or "")
    return SearchResultOut(
        kind="project",
        title=project.title,
        path=f"/projects/{project.slug}",
        subtitle="What We Do > Projects",
        excerpt=excerpt or None,
        image_url=project.thumbnail_url,
    )


def _blog_result(blog: Blog) -> SearchResultOut:
    excerpt = _collapse_text(blog.content)
    return SearchResultOut(
        kind="blog",
        title=blog.title,
        path=f"/blogs/{blog.slug}",
        subtitle=f"Blog > {blog.blog_type.title()}",
        excerpt=excerpt or None,
        image_url=None,
    )


def _project_rank(project: Project, query: str) -> tuple[float, float]:
    score = 0.0
    score += _score_text(project.title, query) * 3
    score += _score_text(project.location, query) * 1.5
    score += _score_text(project.description, query)
    score += _score_text(project.content, query)
    created_ts = project.created_at.timestamp() if project.created_at else 0.0
    return score, created_ts


def _blog_rank(blog: Blog, query: str) -> tuple[float, float]:
    score = 0.0
    score += _score_text(blog.title, query) * 3
    score += _score_text(blog.blog_type, query) * 1.5
    score += _score_text(blog.content, query)
    updated_ts = blog.updated_at.timestamp() if blog.updated_at else 0.0
    return score, updated_ts


def _recommended_items(db: Session, limit: int) -> list[SearchResultOut]:
    featured_projects = (
        db.query(Project)
        .filter(Project.delete_at.is_(None))
        .order_by(Project.is_featured.desc(), Project.created_at.desc(), Project.id.desc())
        .limit(limit)
        .all()
    )

    items = [_project_result(project) for project in featured_projects[:limit]]
    if len(items) >= limit:
        return items[:limit]

    remaining = limit - len(items)
    recent_blogs = (
        db.query(Blog)
        .order_by(Blog.updated_at.desc(), Blog.id.desc())
        .limit(remaining)
        .all()
    )
    items.extend(_blog_result(blog) for blog in recent_blogs)
    return items[:limit]


@router.get("/", response_model=SearchResponseOut)
def search_site(
    q: str = Query("", max_length=120),
    limit: int = Query(8, ge=1, le=20),
    recommended_limit: int = Query(4, ge=1, le=10),
    db: Session = Depends(get_db),
):
    query = _normalize_query(q)
    recommended = _recommended_items(db, recommended_limit)

    if not query:
        return SearchResponseOut(query="", recommended=recommended, results=[], total=0)

    terms = [term for term in query.split(" ") if term]
    like_terms = [f"%{term}%" for term in terms]

    project_filters = []
    for like_term in like_terms:
        project_filters.append(
            or_(
                Project.title.ilike(like_term),
                Project.slug.ilike(like_term),
                Project.location.ilike(like_term),
                Project.description.ilike(like_term),
                Project.content.ilike(like_term),
            )
        )

    blog_filters = []
    for like_term in like_terms:
        blog_filters.append(
            or_(
                Blog.title.ilike(like_term),
                Blog.slug.ilike(like_term),
                Blog.blog_type.ilike(like_term),
                Blog.content.ilike(like_term),
            )
        )

    project_matches = (
        db.query(Project)
        .filter(Project.delete_at.is_(None), *project_filters)
        .order_by(Project.is_featured.desc(), Project.created_at.desc(), Project.id.desc())
        .limit(limit * 2)
        .all()
    )
    blog_matches = (
        db.query(Blog)
        .filter(*blog_filters)
        .order_by(Blog.updated_at.desc(), Blog.id.desc())
        .limit(limit * 2)
        .all()
    )

    ranked = []
    for project in project_matches:
        score, timestamp = _project_rank(project, query)
        if score > 0:
            ranked.append((score, timestamp, 0, _project_result(project)))

    for blog in blog_matches:
        score, timestamp = _blog_rank(blog, query)
        if score > 0:
            ranked.append((score, timestamp, 1, _blog_result(blog)))

    ranked.sort(key=lambda item: (-item[0], -item[1], item[2], item[3].title.lower()))
    results = [item[3] for item in ranked[:limit]]

    return SearchResponseOut(
        query=query,
        recommended=recommended,
        results=results,
        total=len(ranked),
    )
