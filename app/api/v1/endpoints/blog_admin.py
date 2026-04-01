from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.blog_sync_repository import BlogSyncRepository
from app.schemas.blog_sync import BlogDetailOut, BlogTypeUpdateIn, BlogTypeUpdateOut, ImportUrlIn, SyncLogOut, SyncStartedOut, SyncSummaryOut
from app.services.blog_crawler import normalize_blog_type
from app.services.blog_sync_service import BlogSyncService, is_blog_sync_running, run_blog_sync_job
from app.api.v1.endpoints.blogs import _to_blog_list_item

router = APIRouter(prefix="/admin", tags=["Blog Admin"])


@router.post("/sync", response_model=SyncStartedOut, status_code=status.HTTP_202_ACCEPTED)
def trigger_blog_sync(
    background_tasks: BackgroundTasks,
    _: User = Depends(get_current_user),
):
    if is_blog_sync_running():
        raise HTTPException(status_code=409, detail="A blog sync is already running")

    started_at = datetime.now(timezone.utc)
    background_tasks.add_task(run_blog_sync_job)
    return SyncStartedOut(message="Blog sync started", started_at=started_at)


@router.get("/sync/logs", response_model=list[SyncLogOut])
def list_blog_sync_logs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repository = BlogSyncRepository()
    return repository.list_sync_logs(db, limit=limit)


@router.post("/import-excel", response_model=SyncSummaryOut)
async def import_blog_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if is_blog_sync_running():
        raise HTTPException(status_code=409, detail="A blog sync is already running")

    filename = (file.filename or "").lower()
    if not filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    try:
        file_bytes = await file.read()
        summary = BlogSyncService(db).import_from_excel(file_bytes)
        return SyncSummaryOut(**summary.to_dict())
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/import-url", response_model=SyncSummaryOut)
def import_blog_url(
    payload: ImportUrlIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if is_blog_sync_running():
        raise HTTPException(status_code=409, detail="A blog sync is already running")

    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL must not be empty")

    try:
        summary = BlogSyncService(db).import_from_urls([url])
        return SyncSummaryOut(**summary.to_dict())
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/blogs/{blog_id}", response_model=BlogDetailOut)
def get_blog_detail_admin(
    blog_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repository = BlogSyncRepository()
    blog = repository.get_blog_by_id(db, blog_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    summary = _to_blog_list_item(blog)
    return BlogDetailOut(**summary.model_dump(), content=blog.content)


@router.delete("/blogs/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repository = BlogSyncRepository()
    blog = repository.get_blog_by_id(db, blog_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    repository.delete_blog(db, blog)
    db.commit()


@router.patch("/blogs/{blog_id}/type", response_model=BlogTypeUpdateOut)
def update_blog_type(
    blog_id: int,
    payload: BlogTypeUpdateIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    repository = BlogSyncRepository()
    blog = repository.get_blog_by_id(db, blog_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    if payload.type is None:
        blog.type_override = None
        blog.blog_type = blog.source_type
    else:
        resolved_type = normalize_blog_type(payload.type)
        blog.type_override = resolved_type
        blog.blog_type = resolved_type

    db.commit()
    db.refresh(blog)

    return BlogTypeUpdateOut(
        id=blog.id,
        type=blog.blog_type,
        source_type=blog.source_type,
        type_override=blog.type_override,
        is_type_overridden=bool(blog.type_override),
    )
