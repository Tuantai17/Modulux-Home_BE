from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.crud.crud_project import get_projects, get_project, get_project_by_slug, get_featured_projects, create_project, update_project, soft_delete_project
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectOut])
def list_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_projects(db, skip=skip, limit=limit)


@router.get("/featured", response_model=List[ProjectOut])
def list_featured(db: Session = Depends(get_db)):
    return get_featured_projects(db)


@router.get("/slug/{slug}", response_model=ProjectOut)
def get_by_slug(slug: str, db: Session = Depends(get_db)):
    obj = get_project_by_slug(db, slug)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return obj


@router.get("/{project_id}", response_model=ProjectOut)
def get_one(project_id: int, db: Session = Depends(get_db)):
    obj = get_project(db, project_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return obj


@router.post("/", response_model=ProjectOut, status_code=201)
def create(data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_project(db, data, author_id=current_user.id)


@router.put("/{project_id}", response_model=ProjectOut)
def update(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_project(db, project_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    return obj


@router.delete("/{project_id}", status_code=204)
def delete(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_project(db, project_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")
    soft_delete_project(db, project_id, deleted_by=current_user.id)
