from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from typing import Annotated
import jwt
from starlette import status
from datetime import datetime, timezone
from jwt.exceptions import InvalidTokenError
from movies.models import User


bcrypt_context = CryptContext(schemes=["bcrypt"])
ALGORITHM = "HS256"
SECRET_KEY = "5105c20de654f18c9a7a9d18ee8f1b0f3e796c4287d91dd0d60475050e02ca81"
DB_URL = "sqlite:///movies.db"
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_user_from_db(username):
    """ Returns existing user or None """
    db = SessionLocal()
    orm_select_statement = select(User).where(User.username == username)
    existing_user = db.execute(orm_select_statement).scalar_one_or_none()
    return existing_user


def authenticate_user(username, password):
    existing_user = get_user_from_db(username)
    if existing_user is None:
        return None
    if not bcrypt_context.verify(password, existing_user.hashed_password):
        return None
    return existing_user


def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/user/login"))]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing u/name")
        expires = payload.get("exp")
        if datetime.now(timezone.utc) > datetime.fromtimestamp(expires, timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token error")

    user = get_user_from_db(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
