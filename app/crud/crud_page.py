from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone

from app.models.page import Page, Faq, PageSection
from app.schemas.page import PageCreate, PageUpdate, FaqCreate, FaqUpdate, PageSectionCreate, PageSectionUpdate

_now = lambda: datetime.now(timezone.utc)


# ─── Page ────────────────────────────────────────────────────────
def get_pages(db: Session):
    return db.query(Page).options(joinedload(Page.sections)).filter(Page.delete_at == None).all()


def get_page(db: Session, page_id: int):
    return db.query(Page).options(joinedload(Page.sections)).filter(Page.id == page_id, Page.delete_at == None).first()


def get_page_by_slug(db: Session, slug: str):
    return db.query(Page).options(joinedload(Page.sections)).filter(Page.slug == slug, Page.delete_at == None).first()


def create_page(db: Session, data: PageCreate, author_id: int):
    obj = Page(**data.model_dump(), author_id=author_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_page(db: Session, page_id: int, data: PageUpdate):
    obj = get_page(db, page_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_page(db: Session, page_id: int, deleted_by: int):
    obj = get_page(db, page_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
    return obj


# ─── PageSection ────────────────────────────────────────────────
def create_page_section(db: Session, page_id: int, data: PageSectionCreate):
    obj = PageSection(page_id=page_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_page_section(db: Session, section_id: int):
    return db.query(PageSection).filter(PageSection.id == section_id).first()


def update_page_section(db: Session, section_id: int, data: PageSectionUpdate):
    obj = get_page_section(db, section_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def delete_page_section(db: Session, section_id: int):
    obj = get_page_section(db, section_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj


# ─── Faq ─────────────────────────────────────────────────────────
def get_faqs(db: Session):
    return db.query(Faq).filter(Faq.delete_at == None).order_by(Faq.display_order).all()


def get_faq(db: Session, faq_id: int):
    return db.query(Faq).filter(Faq.id == faq_id, Faq.delete_at == None).first()


def create_faq(db: Session, data: FaqCreate):
    obj = Faq(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_faq(db: Session, faq_id: int, data: FaqUpdate):
    obj = get_faq(db, faq_id)
    if obj:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj


def soft_delete_faq(db: Session, faq_id: int, deleted_by: int):
    obj = get_faq(db, faq_id)
    if obj:
        obj.delete_at = _now()
        obj.delete_by = deleted_by
        db.commit()
    return obj
