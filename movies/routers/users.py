from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy import insert
from sqlalchemy.orm import Session
from starlette import status
from movies.utils import get_db_session, get_user_from_db, bcrypt_context, authenticate_user, ALGORITHM, SECRET_KEY, get_current_user
from movies.models import User, UserRequest, JWTToken
from datetime import datetime, timedelta, timezone
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import jwt


router = APIRouter(prefix="/user", tags=["user"])


# API Endpoints
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_new_user(new_user: UserRequest, db: Annotated[Session, Depends(get_db_session)]):
    """ Register a new user """
    existing_user = get_user_from_db(new_user.username)
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username exists.")
    insert_orm_statement = insert(User).values(
            username=new_user.username,
            email=new_user.email,
            hashed_password=bcrypt_context.hash(new_user.password)
            )
    db.execute(insert_orm_statement)
    db.commit()


# Authenticate user
@router.post("/login", response_model=JWTToken)
async def login(login_form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """ Login and return the JWT token. """
    user = authenticate_user(login_form.username, login_form.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    to_encrypt = {"sub": user.username}
    exp_time = datetime.now(timezone.utc) + timedelta(minutes=3)
    to_encrypt.update({"exp": exp_time})
    encoded_jwt = jwt.encode(to_encrypt, SECRET_KEY, ALGORITHM)
    return JWTToken(access_token=encoded_jwt, token_type="Bearer")


# Get my info
@router.get("/me", status_code=status.HTTP_200_OK)
async def me(current_user: Annotated[User, Depends(get_current_user)]):
    """ Return authenticated user information """
    return current_user
