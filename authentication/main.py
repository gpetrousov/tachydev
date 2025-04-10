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


async def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="login"))]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_expired_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired."
            )
    try:
        # Verify username JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"payload: {payload}")
        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Verify JWT token did not expire
        expires = payload.get("exp")
        if datetime.now(tz=timezone.utc) > datetime.fromtimestamp(expires, tz=timezone.utc):
            raise token_expired_exception

        token_data = TokenData(username=username)
        print(f"token_data: {token_data}")
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_from_db(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User inactive")
    return current_user

app = FastAPI()


def get_user_from_db(username):
    if username in users_db:
        user = UserInDB(**users_db[username])
        return user


def authenticate_user(username, password):
    """ Authenticates the user if they exist. """
    # 1.1 Verify user exists in database
    user = get_user_from_db(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    # 1.2 Verify password is same as hashed password

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password")
    return user


@app.get("/items/")
async def read_all(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="login"))]):
    """
    Unprotected endpoint. Just expected the Authorization header to be present.
    curl -X 'GET' \
          'http://127.0.0.1:8000/items/' \
          -H 'accept: application/json' \
          -H 'Authorization: BEARER f@k3T0k3N'
    """
    return {"token": token}


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticates the client and retursn a JWT token.
    curl -L -X 'POST' \
            'http://127.0.0.1:8000/login' \
            -H 'Content-TYpe: application/x-www-form-urlencoded' \
            -d "username=bob&password=secret1"
    """
    # 1. Authenticate user
    user = authenticate_user(form_data.username, form_data.password)
    print(f"user: {user}")

    # 2. Create JWT access token
    token_data = {"sub": user.username}
    expiration_time = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    token_data.update({"exp": expiration_time})
    encoded_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    # 3. Return access token
    return Token(access_token=encoded_token, token_type="Bearer")


@app.get("/protected")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Protected endpoint. Expects a valid JWT token and performs verification.
    curl -L -X 'GET' \
  'http://127.0.0.1:8000/protected' \
          -H 'accept: application/json' \
          -H 'Authorization: BEARER eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJib2IiLCJleHAiOjE3NDQyNzkzMTJ9.WWHP9nTFpGfyfcpTrgPxwwZDwyV_mGbeE7qV2lK8glI'
    """
    return current_user
