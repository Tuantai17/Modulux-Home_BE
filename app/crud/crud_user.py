from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id, User.delete_at == None).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username, User.delete_at == None).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email, User.delete_at == None).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.delete_at == None).offset(skip).limit(limit).all()


def create_user(db: Session, data: UserCreate):
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def soft_delete_user(db: Session, user_id: int, deleted_by: int):
    user = get_user(db, user_id)
    if user:
        user.delete_at = datetime.now(timezone.utc)
        user.delete_by = deleted_by
        db.commit()
    return user
