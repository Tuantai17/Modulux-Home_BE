from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.contact import SubscriberCreate, SubscriberOut
from app.crud.crud_contact import get_subscribers, get_subscriber, get_subscriber_by_email, create_subscriber, soft_delete_subscriber
from app.models.user import User

router = APIRouter(prefix="/subscribers", tags=["Subscribers"])


@router.get("/", response_model=List[SubscriberOut])
def list_subscribers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Admin only: liệt kê danh sách đăng ký nhận tin."""
    return get_subscribers(db, skip=skip, limit=limit)


@router.post("/", response_model=SubscriberOut, status_code=201)
def subscribe(data: SubscriberCreate, db: Session = Depends(get_db)):
    """Public: đăng ký nhận bản tin."""
    existing = get_subscriber_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already subscribed")
    return create_subscriber(db, data)


@router.delete("/{subscriber_id}", status_code=204)
def delete(subscriber_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_subscriber(db, subscriber_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    soft_delete_subscriber(db, subscriber_id, deleted_by=current_user.id)
