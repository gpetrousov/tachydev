from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Annotated
from passlib.context import CryptContext


users_db = {
        "bob": {
            "username": "bob",
            "full_name": "bob martin",
            "email": "bob@martin.com",
            "hashed_password": "fakehashedsecret1",
            "disabled": False,
            },
        "alice": {
            "username": "alice",
            "full_namae": "alice stone",
            "email": "alice@stone.com",
            "hashed_password": "fakehashedsecret2",
            "disabled": True,
            }
        }


class User(BaseModel):
    username: str
    email: str = Field(default=None)
    full_name: str = Field(default=None)
    disabled: bool = Field(default=None)


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_password: str):
    pwd_context.hash(plain_password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(users_db, username: str, password: str):
    user = get_user(users_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def fake_decode_token(token):
    user = get_user(users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="token"))]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User inactive")
    return current_user


def get_hashed_password(password: str):
    return "fakehashed" + password


app = FastAPI()


@app.get("/items/")
async def read_all(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="token"))]):
    return {"token": token}


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect u/name of p/word")
    user = UserInDB(**user_dict)
    hashed_password = get_hashed_password(form_data.password)
    if hashed_password != user.hashed_password:
        raise HTTPException(status=status.HTTP_400_BAD_REQUEST, detail="Incorrect u/name or p/word")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
