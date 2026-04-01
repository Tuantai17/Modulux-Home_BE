from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import os

from app.core.config import MEDIA_ROOT, MEDIA_BASE_URL

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.page import (
    PageCreate, PageUpdate, PageOut, 
    PageSectionCreate, PageSectionUpdate, PageSectionOut
)
from app.crud.crud_page import (
    get_pages, get_page, get_page_by_slug, create_page, update_page, soft_delete_page,
    create_page_section, update_page_section, delete_page_section
)
from app.models.user import User

router = APIRouter(prefix="/pages", tags=["Pages"])


@router.get("/", response_model=List[PageOut])
def list_pages(db: Session = Depends(get_db)):
    return get_pages(db)


@router.get("/slug/{slug}", response_model=PageOut)
def get_by_slug(slug: str, db: Session = Depends(get_db)):
    obj = get_page_by_slug(db, slug)
    if not obj:
        raise HTTPException(status_code=404, detail="Page not found")
    return obj


@router.get("/{page_id}", response_model=PageOut)
def get_one(page_id: int, db: Session = Depends(get_db)):
    obj = get_page(db, page_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Page not found")
    return obj


@router.post("/", response_model=PageOut, status_code=201)
def create(data: PageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_page(db, data, author_id=current_user.id)


@router.put("/{page_id}", response_model=PageOut)
def update(page_id: int, data: PageUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_page(db, page_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Page not found")
    return obj


@router.delete("/{page_id}", status_code=204)
def delete(page_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_page(db, page_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Page not found")
    soft_delete_page(db, page_id, deleted_by=current_user.id)


# ─── Page Section Management (Admin) ──────────────────────────
@router.post("/{page_id}/sections", response_model=PageSectionOut, status_code=201)
def add_section(
    page_id: int, 
    data: PageSectionCreate, 
    db: Session = Depends(get_db), 
    _: User = Depends(get_current_user)
):
    return create_page_section(db, page_id, data)


@router.put("/sections/{section_id}", response_model=PageSectionOut)
def update_section(
    section_id: int, 
    data: PageSectionUpdate, 
    db: Session = Depends(get_db), 
    _: User = Depends(get_current_user)
):
    obj = update_page_section(db, section_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Section not found")
    return obj


@router.delete("/sections/{section_id}", status_code=204)
def delete_section(
    section_id: int, 
    db: Session = Depends(get_db), 
    _: User = Depends(get_current_user)
):
    delete_page_section(db, section_id)
    return None


@router.post("/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_page_image(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user)
):
    """
    Upload an image for a page section.
    """
    PAGES_UPLOAD_DIR = MEDIA_ROOT / "pages"
    PAGES_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    generated_name = f"{uuid.uuid4().hex}{ext}"
    destination_path = PAGES_UPLOAD_DIR / generated_name

    # Check if directory exists and write file
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded image is empty")
        
        with open(destination_path, "wb") as f:
            f.write(content)
            
        # Return the public URL
        relative_url = f"/pages/{generated_name}"
        return {
            "url": f"{MEDIA_BASE_URL.rstrip('/')}{relative_url}",
            "relative_url": f"/media{relative_url}"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {str(e)}")
