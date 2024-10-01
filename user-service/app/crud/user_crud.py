from sqlmodel import Session, select
from app.models.user_model import User, UserCreate
from app.auth.user_auth import get_password_hash
from typing import Optional

def create_user(user_create: UserCreate, session: Session) -> User:
    hashed_password = get_password_hash(user_create.password)
    user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_username(username: str, session: Session) -> Optional[User]:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    return user

def get_all_users(session: Session) -> list[User]:
    statement = select(User)
    users = session.exec(statement).all()
    return users

#Validate User By Id
def get_user_by_id(user_id: int, session: Session) -> Optional[User]:
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user