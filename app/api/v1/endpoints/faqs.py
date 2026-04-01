from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.page import FaqCreate, FaqUpdate, FaqOut
from app.crud.crud_page import get_faqs, get_faq, create_faq, update_faq, soft_delete_faq
from app.models.user import User

router = APIRouter(prefix="/faqs", tags=["FAQs"])


@router.get("/", response_model=List[FaqOut])
def list_faqs(db: Session = Depends(get_db)):
    return get_faqs(db)


@router.get("/{faq_id}", response_model=FaqOut)
def get_one(faq_id: int, db: Session = Depends(get_db)):
    obj = get_faq(db, faq_id)
    if not obj:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return obj


@router.post("/", response_model=FaqOut, status_code=201)
def create(data: FaqCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return create_faq(db, data)


@router.put("/{faq_id}", response_model=FaqOut)
def update(faq_id: int, data: FaqUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    obj = update_faq(db, faq_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return obj


@router.delete("/{faq_id}", status_code=204)
def delete(faq_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obj = get_faq(db, faq_id)
    if not obj:
        raise HTTPException(status_code=404, detail="FAQ not found")
    soft_delete_faq(db, faq_id, deleted_by=current_user.id)
