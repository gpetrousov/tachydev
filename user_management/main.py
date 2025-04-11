from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Annotated
from datetime import datetime, timezone, timedelta
from jwt import encode

ALGORITHM = "HS256"
SECRET_KEY = "48e3e8917fc1aa0569121e0b95923ef8e9978e7cacb7f113968bed6942788f83"


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    password: str
    email: EmailStr
    active: bool = True
    id: int = 0


class UserInDB(User):
    hashed_pasword: str


class UserRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
    email: str = Field(min_length=4)


USERS_DB = []


app = FastAPI()


@app.get("/")
async def get_users():
    return USERS_DB


# Create
def set_user_id(user: User):
    user.id = USERS_DB[-1].id + 1 if len(USERS_DB) > 0 else 1


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_new_user(new_user: UserRequest):
    """ Register new user and add to the database """
    new_user = User(**new_user.model_dump())
    set_user_id(new_user)
    USERS_DB.append(new_user)


def hash_password(password):
    return f"hashed({password})hashed"


def authenticate_user(username, password):
    """
    Validate username
    Validate password
    """

    # Validate username
    existing_user = None
    for u in USERS_DB:
        if u.uname == username:
            existing_user = UserInDB(**u)
            break
    if existing_user is None:
        return None

    # Validate password
    if existing_user.hashed_password != hash_password(password):
        return None

    return existing_user


@app.post("/login")
async def login(login_form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """ Login and return JWT token """

    # Authenticate user
    user = authenticate_user(login_form.username, login_form.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    # Create JWT token
    to_encrypt = {"sub": user.uname}
    exp_time = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encrypt.update({"exp": exp_time})
    encoded_jwt = encode(to_encrypt, SECRET_KEY, ALGORITHM)
    return JWTToken(access_token=encoded_jwt, token_type="Bearer")


# Read
@app.get("/me")
async def get_me():
    """ Get my information """
    pass


# Update
@app.put("/update")
async def update_me():
    """ Update my information """


# Delete
@app.put("/delete")
async def delete_me():
    """ Delete my user record """
    pass
    pass
