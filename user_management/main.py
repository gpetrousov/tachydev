from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field, EmailStr
from typing import Annotated
from datetime import datetime, timezone, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

ALGORITHM = "HS256"
SECRET_KEY = "48e3e8917fc1aa0569121e0b95923ef8e9978e7cacb7f113968bed6942788f83"
USERS_DB = []
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    active: bool = True
    id: int


class UserRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
    email: str = Field(min_length=4)

    model_config = {
            "json_schema_extra": {
                "example": {
                    "username": "ioannis",
                    "password": "ioannis123",
                    "email": "contact@petrousoft.com"
                    }
                }
            }


app = FastAPI()


@app.get("/")
async def get_users():
    """ Return the usersDB - unprotected endpoint """
    return USERS_DB


def set_user_id():
    print("Set id")
    if len(USERS_DB) > 0:
        return USERS_DB[-1].id + 1
    else:
        return 1


def get_user_from_db(username):
    for u in USERS_DB:
        if username == u.username:
            return u


async def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="login"))]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="U/name missing.")
        expires = payload.get("exp")
        if datetime.now(timezone.utc) > datetime.fromtimestamp(expires, timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token error.")

    user = get_user_from_db(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="U/name not found")
    return user


# Create
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_new_user(new_user: UserRequest):
    """ Register new user and add to the database """
    if get_user_from_db(new_user.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username exists")
    new_user = User(
            username=new_user.username,
            hashed_password=bcrypt_context.hash(new_user.password),
            email=new_user.email,
            id=set_user_id()
            )
    USERS_DB.append(new_user)
    return new_user


def authenticate_user(username, password):
    """ Validate username;Validate password """

    # Validate username
    existing_user = None
    for u in USERS_DB:
        if u.username == username:
            existing_user = u
            break
    if existing_user is None:
        return None

    # Validate password
    if not bcrypt_context.verify(password, existing_user.hashed_password):
        return None

    return u


@app.post("/login", response_model=JWTToken)
async def login(login_form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """ Login and return JWT token """

    # Authenticate user
    user = authenticate_user(login_form.username, login_form.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    # Create JWT token
    to_encrypt = {"sub": user.username}
    exp_time = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encrypt.update({"exp": exp_time})
    encoded_jwt = jwt.encode(to_encrypt, SECRET_KEY, ALGORITHM)

    return JWTToken(access_token=encoded_jwt, token_type="Bearer")


# Read
@app.get("/me", status_code=status.HTTP_200_OK)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """ Get my user information """
    return current_user


# Update
@app.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_me(current_user: Annotated[User, Depends(get_current_user)], updated_user: UserRequest):
    """ Update my user information """
    print(f"Update user: {updated_user}")
    if get_user_from_db(updated_user.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username exists")
    current_user.username = updated_user.username
    current_user.hashed_password = bcrypt_context.hash(updated_user.password)
    current_user.email = updated_user.email


# Delete
def delete_user(username):
    for i in range(len(USERS_DB)):
        if USERS_DB[i].username == username:
            USERS_DB.pop(i)
            break


@app.put("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: Annotated[User, Depends(get_current_user)]):
    """ Delete my user record """
    delete_user(current_user.username)
