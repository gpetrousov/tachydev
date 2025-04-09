from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Annotated
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone

ALGORITHM = "HS256"
SECRET_KEY = "d2c5d48991e5f6ffe09e659a805813717313a13bb005d9a7055623c02cfc7f31"

users_db = {
        "bob": {
            "username": "bob",
            "full_name": "bob martin",
            "email": "bob@martin.com",
            "hashed_password": "$2b$12$092Qr9EwWKgDIyE35wY41eR4ey1M5Ev.195W6IiTFIIS.yu5HKuCG", # secret1
            "disabled": False,
            },
        "alice": {
            "username": "alice",
            "full_namae": "alice stone",
            "email": "alice@stone.com",
            "hashed_password": "$2b$12$Hu5ymcdWtJ82brU0clz2J.DLSdKQelR7o2q.ofurK6ja/mNOpSQXK", # secret2
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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"payload: {payload}")
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        print(f"token_data: {token_data}")
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(users_db, token_data.username)
    if user is None:
        raise credentials_exception
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
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})

    # Create access token
    access_token_expiration_delta = timedelta(minutes=30)
    data = {"sub": user.username}
    to_encode = data.copy()
    if access_token_expiration_delta:
        expire = datetime.now(timezone.utc) + access_token_expiration_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Return access token
    return Token(access_token=encoded_jwt, token_type="bearer")


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
