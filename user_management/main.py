from fastapi import FastAPI, status, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime, timezone, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker
from sqlalchemy import Integer, String, Boolean, create_engine, select, insert, update, delete
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

ALGORITHM = "HS256"
SECRET_KEY = "48e3e8917fc1aa0569121e0b95923ef8e9978e7cacb7f113968bed6942788f83"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine("sqlite:///user_management.db", echo=True)


class Base(DeclarativeBase):
    pass


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class User(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(8))
    email: Mapped[str] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True)


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


Base.metadata.create_all(bind=engine)
Session = sessionmaker(engine)
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# READ - SELECT
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse(request=request, name="homepage.html")


def get_user_from_db(username):
    orm_statement = select(User).where(User.username == username)
    with Session() as sess:
        try:
            existing_user = sess.execute(orm_statement).scalar_one_or_none()
        except Exception as e:
            print(f"get_user_from_db: {e}")
    return existing_user


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


# CREATE - INSERT
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """ Server the registration page """
    return templates.TemplateResponse(request=request, name="register.html")


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_new_user(new_user: UserRequest):
    """ Register new user and add to the database """
    existing_user = get_user_from_db(new_user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User exists")
    insert_orm_statement = insert(User).values(
            username=new_user.username,
            email=new_user.email,
            hashed_password=bcrypt_context.hash(new_user.password)
            )
    with Session() as sess:
        try:
            sess.execute(insert_orm_statement)
            sess.commit()
        except Exception as e:
            print(f"register_new_user: {e}")


def authenticate_user(username, password):
    """ Validate username;Validate password """

    # Validate username
    existing_user = get_user_from_db(username)
    if existing_user is None:
        return None

    # Validate password
    if not bcrypt_context.verify(password, existing_user.hashed_password):
        return None

    return existing_user


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """ Custom HTTPException handler for credentials error. """
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credentials Error."}, status_code=exc.status_code)

    # For other HTTPExceptions, you might want to render a generic error page
    return HTMLResponse(f"<h1>HTTP Error {exc.status_code}</h1><p>{exc.detail}</p>", status_code=exc.status_code)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """ Serves the login page """
    return templates.TemplateResponse(request=request, name="login.html")


@app.post("/login", response_model=JWTToken)
async def login(login_form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """ Login and return JWT token """

    # Authenticate user
    user = authenticate_user(login_form.username, login_form.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong username or password.")

    # Create JWT token
    to_encrypt = {"sub": user.username}
    exp_time = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encrypt.update({"exp": exp_time})
    encoded_jwt = jwt.encode(to_encrypt, SECRET_KEY, ALGORITHM)

    return JWTToken(access_token=encoded_jwt, token_type="Bearer")


# READ - SELECT
@app.get("/me", status_code=status.HTTP_200_OK)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """ Get my user information """
    return current_user


# UPDATE - SELECT - UPDATE
@app.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_me(current_user: Annotated[User, Depends(get_current_user)], updated_user: UserRequest):
    """ Update my user information """
    print(f"Update user: {updated_user}")
    orm_update_statement = update(User).where(User.username == current_user.username).values(
            username=updated_user.username,
            email=updated_user.email,
            hashed_password=bcrypt_context.hash(updated_user.password)
            )
    with Session() as sess:
        try:
            sess.execute(orm_update_statement)
            sess.commit()
        except Exception as e:
            print(f"update_me: {e}")


def delete_user(username):
    orm_delete_statement = delete(User).where(User.username == username)
    with Session() as sess:
        try:
            sess.execute(orm_delete_statement)
            sess.commit()
        except Exception as e:
            print(f"delete_user: {e}")


# DELETE - DELETE
@app.put("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: Annotated[User, Depends(get_current_user)]):
    """ Delete my user record """
    delete_user(current_user.username)
