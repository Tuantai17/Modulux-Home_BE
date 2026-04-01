from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
from uuid import uuid4

from app.db.session import get_db
from app.api.deps import get_current_user
from app.core.config import MEDIA_BASE_URL, MEDIA_ROOT
from app.schemas.site import PartnerCreate, PartnerUpdate, PartnerOut
from app.crud.crud_site import get_partners, get_partner, create_partner, update_partner, soft_delete_partner
from app.models.user import User

router = APIRouter(prefix="/partners", tags=["Partners"])

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".svg"}
PARTNER_UPLOAD_DIR = MEDIA_ROOT / "partners"

@router.post("/upload-logo", status_code=status.HTTP_201_CREATED)
async def upload_logo(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
):
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .jpg, .jpeg, .png, .webp, .svg, and .avif images are supported",
        )

    PARTNER_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    generated_name = f"partner-{uuid4().hex}{extension}"
    destination_path = PARTNER_UPLOAD_DIR / generated_name

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded image is empty")

    destination_path.write_bytes(file_bytes)
    relative_path = f"/media/partners/{generated_name}"

    return {
        "url": f"{MEDIA_BASE_URL}/partners/{generated_name}",
        "relative_url": relative_path,
        "filename": generated_name,
    }


@router.get("/", response_model=List[PartnerOut])
def list_partners(db: Session = Depends(get_db)):
    return get_partners(db)


@router.get("/{partner_id}", response_model=PartnerOut)
def get_one(partner_id: int, db: Session = Depends(get_db)):
    obj = get_partner(db, partner_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Partner not found")
    return obj


@router.post("/", response_model=PartnerOut, status_code=201)
def create(data: PartnerCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return create_partner(db, data)


@router.put("/{partner_id}", response_model=PartnerOut)
def update(partner_id: int, data: PartnerUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_partner(db, partner_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Partner not found")
    return obj


@router.delete("/{partner_id}", status_code=204)
def delete(partner_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_partner(db, partner_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Partner not found")
    soft_delete_partner(db, partner_id, deleted_by=current_user.id)
