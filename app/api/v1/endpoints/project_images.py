from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.project import ProjectImageCreate, ProjectImageUpdate, ProjectImageOut
from app.crud.crud_project import get_project_images, get_project_image, create_project_image, update_project_image, soft_delete_project_image
from app.models.user import User

router = APIRouter(prefix="/project-images", tags=["Project Images"])


@router.get("/project/{project_id}", response_model=List[ProjectImageOut])
def list_by_project(project_id: int, db: Session = Depends(get_db)):
    return get_project_images(db, project_id)


@router.get("/{image_id}", response_model=ProjectImageOut)
def get_one(image_id: int, db: Session = Depends(get_db)):
    obj = get_project_image(db, image_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Image not found")
    return obj


@router.post("/", response_model=ProjectImageOut, status_code=201)
def create(data: ProjectImageCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return create_project_image(db, data)


@router.put("/{image_id}", response_model=ProjectImageOut)
def update(image_id: int, data: ProjectImageUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_project_image(db, image_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Image not found")
    return obj


@router.delete("/{image_id}", status_code=204)
def delete(image_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_project_image(db, image_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Image not found")
    soft_delete_project_image(db, image_id, deleted_by=current_user.id)
