from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import MEDIA_BASE_URL, MEDIA_ROOT
from app.db.session import get_db
from app.schemas.site import VideoCreate, VideoOut, VideoUpdate
from app.crud.crud_site import (
    create_video,
    get_video,
    get_videos,
    get_videos_for_admin,
    soft_delete_video,
    update_video,
)
from app.models.user import User

router = APIRouter(prefix="/videos", tags=["Videos"])

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
VIDEO_UPLOAD_DIR = MEDIA_ROOT / "videos"
VIDEO_LOCATIONS = {"home", "faq", "both"}


def _normalize_location(location: Optional[str], default: str = "home") -> str:
    normalized_location = (location or default).strip().lower()
    if normalized_location not in VIDEO_LOCATIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="location must be one of: home, faq, both",
        )
    return normalized_location


async def _save_uploaded_image(file: UploadFile, folder: str) -> dict:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .jpg, .jpeg, .png, .webp, and .avif images are supported",
        )

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image",
        )

    destination_dir = VIDEO_UPLOAD_DIR / folder
    destination_dir.mkdir(parents=True, exist_ok=True)

    generated_name = f"{folder}-{uuid4().hex}{extension}"
    destination_path = destination_dir / generated_name

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded image is empty")

    destination_path.write_bytes(file_bytes)
    relative_path = f"/media/videos/{folder}/{generated_name}"

    return {
        "url": f"{MEDIA_BASE_URL}/videos/{folder}/{generated_name}",
        "relative_url": relative_path,
        "filename": generated_name,
    }


@router.get("/", response_model=List[VideoOut])
def list_videos(
    location: str = "home",
    db: Session = Depends(get_db),
):
    return get_videos(db, location=_normalize_location(location))


@router.get("/admin", response_model=List[VideoOut])
def list_videos_for_admin(
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    normalized_location = None
    if location is not None and location.strip() != "":
        normalized_location = _normalize_location(location)
    return get_videos_for_admin(db, location=normalized_location)


@router.post("/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_video_image(
    kind: str,
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
):
    normalized_kind = (kind or "").strip().lower()
    if normalized_kind not in {"poster", "thumbnail"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="kind must be poster or thumbnail")

    return await _save_uploaded_image(file, normalized_kind)


@router.get("/{video_id}", response_model=VideoOut)
def get_one(video_id: int, db: Session = Depends(get_db)):
    obj = get_video(db, video_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Video not found")
    return obj


@router.post("/", response_model=VideoOut, status_code=201)
def create(data: VideoCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return create_video(db, data)


@router.put("/{video_id}", response_model=VideoOut)
def update(video_id: int, data: VideoUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_video(db, video_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Video not found")
    return obj


@router.delete("/{video_id}", status_code=204)
def delete(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_video(db, video_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Video not found")
    soft_delete_video(db, video_id, deleted_by=current_user.id)
