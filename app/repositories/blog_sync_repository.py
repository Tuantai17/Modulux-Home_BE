from sqlalchemy.orm import Session

from app.models.blog_sync import Blog, SyncLog


class BlogSyncRepository:
    def list_blogs(self, db: Session, *, page: int, page_size: int) -> tuple[list[Blog], int]:
        query = db.query(Blog).order_by(Blog.updated_at.desc(), Blog.id.desc())
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_blog_by_slug(self, db: Session, slug: str) -> Blog | None:
        return db.query(Blog).filter(Blog.slug == slug).first()

    def get_blog_by_id(self, db: Session, blog_id: int) -> Blog | None:
        return db.query(Blog).filter(Blog.id == blog_id).first()

    def get_blog_by_source_url(self, db: Session, source_url: str) -> Blog | None:
        return db.query(Blog).filter(Blog.source_url == source_url).first()

    def slug_exists(self, db: Session, slug: str, *, exclude_blog_id: int | None = None) -> bool:
        query = db.query(Blog).filter(Blog.slug == slug)
        if exclude_blog_id is not None:
            query = query.filter(Blog.id != exclude_blog_id)
        return db.query(query.exists()).scalar()

    def add_blog(self, db: Session, blog: Blog) -> Blog:
        db.add(blog)
        return blog

    def add_sync_log(self, db: Session, log: SyncLog) -> SyncLog:
        db.add(log)
        return log

    def delete_blog(self, db: Session, blog: Blog) -> None:
        db.delete(blog)

    def list_sync_logs(self, db: Session, *, limit: int) -> list[SyncLog]:
        return (
            db.query(SyncLog)
            .order_by(SyncLog.created_at.desc(), SyncLog.id.desc())
            .limit(limit)
            .all()
        )
