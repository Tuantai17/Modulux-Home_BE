from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.project import Project, ProjectImage
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectImageCreate, ProjectImageUpdate

_now = lambda: datetime.now(timezone.utc)


# ─── Project ─────────────────────────────────────────────────────
def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Project)
        .filter(Project.delete_at == None)
        .offset(skip).limit(limit)
        .all()
    )


def get_featured_projects(db: Session):
    return db.query(Project).filter(Project.delete_at == None, Project.is_featured == True).all()


def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id, Project.delete_at == None).first()


def get_project_by_slug(db: Session, slug: str):
    return db.query(Project).filter(Project.slug == slug, Project.delete_at == None).first()


def create_project(db: Session, data: ProjectCreate, author_id: int):
    obj = Project(**data.model_dump(), author_id=author_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_project(db: Session, project_id: int, data: ProjectUpdate):
    obj = get_project(db, project_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_project(db: Session, project_id: int, deleted_by: int):
    obj = get_project(db, project_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj


# ─── ProjectImage ────────────────────────────────────────────────
def get_project_images(db: Session, project_id: int):
    return (
        db.query(ProjectImage)
        .filter(ProjectImage.project_id == project_id, ProjectImage.delete_at == None)
        .order_by(ProjectImage.display_order)
        .all()
    )


def get_project_image(db: Session, image_id: int):
    return db.query(ProjectImage).filter(ProjectImage.id == image_id, ProjectImage.delete_at == None).first()


def create_project_image(db: Session, data: ProjectImageCreate):
    obj = ProjectImage(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_project_image(db: Session, image_id: int, data: ProjectImageUpdate):
    obj = get_project_image(db, image_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_project_image(db: Session, image_id: int, deleted_by: int):
    obj = get_project_image(db, image_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj
