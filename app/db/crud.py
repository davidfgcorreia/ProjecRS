from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
import hashlib
from typing import Optional, List

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_email_and_password(db: Session, email: str, password: str) -> Optional[User]:
    hashed_pw = hash_password(password)
    return db.query(User).filter(User.email == email, User.password == hashed_pw).first()

def get_users(db: Session, skip: int = 0, limit: int = 10) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=getattr(user, 'role', 'user')
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserCreate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if db_user:
        setattr(db_user, "name", user.name)
        setattr(db_user, "email", user.email)
        if hasattr(user, 'password') and user.password:
            setattr(db_user, "password", hash_password(user.password))
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> None:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
