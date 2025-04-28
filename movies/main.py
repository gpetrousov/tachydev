from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, create_engine, insert, select, delete
from typing import List, Annotated
from fastapi import FastAPI, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from starlette import status
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
import jwt
from jwt. exceptions import InvalidTokenError


class Base(DeclarativeBase):
    pass


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True)
    username: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(8))
    email: Mapped[str] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    movies: Mapped[List["Movie"]] = relationship()


class UserRequest(BaseModel):
    username: str = Field(min_length=4)
    password: str = Field(min_length=8)
    email: str = Field(min_length=8)

    model_config = {
            "json_schema_extra": {
                "example": {
                    "username": "Peter Jackson",
                    "password": "peter123",
                    "email": "pjackson@lotr.com"
                    }
                }
            }


class Movie(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class MovieRequest(BaseModel):
    name: str = Field(min_length=4)
    year: int = Field()
    rating: float = Field()


app = FastAPI()
DB_URL = "sqlite:///movies.db"
engine = create_engine(DB_URL, echo=True)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
bcrypt_context = CryptContext(schemes=["bcrypt"])
ALGORITHM = "HS256"
SECRET_KEY = "5105c20de654f18c9a7a9d18ee8f1b0f3e796c4287d91dd0d60475050e02ca81"


# Utils
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


def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="login"))]):
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


# API Endpoints
@app.post("/register", status_code=status.HTTP_201_CREATED)
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
@app.post("/login", response_model=JWTToken)
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
@app.get("/me", status_code=status.HTTP_200_OK)
async def me(current_user: Annotated[User, Depends(get_current_user)]):
    """ Return authenticated user information """
    return current_user


# Create new movie
@app.post("/add", status_code=status.HTTP_201_CREATED)
async def create_movie(current_user: Annotated[User, Depends(get_current_user)], new_movie: MovieRequest, db: Annotated[Session, Depends(get_db_session)]):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fobridden")

    insert_orm_statement = insert(Movie).values(
            **new_movie.model_dump(),
            owner_id=current_user.id
            )
    db.execute(insert_orm_statement)
    db.commit()


# Get my movies
@app.get("/movies")
async def get_my_movies(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db_session)]):
    orm_select_statement = select(Movie).where(Movie.owner_id == current_user.id)
    result = db.execute(orm_select_statement)
    return result.scalars().all()


# Get my movie by ID
@app.get("/movies/{movie_id}")
async def get_movie_by_id(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db_session)], movie_id: int = Path()):
    orm_select_statement = select(Movie).where(Movie.owner_id == current_user.id).where(Movie.id == movie_id)
    result = db.execute(orm_select_statement)
    movie_item = result.scalar_one_or_none()
    return movie_item


# Update my movie by ID
@app.put("/movies/update/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_movie_by_id(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db_session)], movie_req: MovieRequest, movie_id: int = Path()):
    orm_select_statement = select(Movie).where(Movie.id == movie_id).where(Movie.owner_id == current_user.id)
    result = db.execute(orm_select_statement)
    movie_item = result.scalar_one_or_none()
    if movie_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid movie ID")
    for k, v in movie_req.model_dump().items():
        setattr(movie_item, k, v)
    db.commit()


# Delete my movie by ID
@app.delete("/movies/delete/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie_by_id(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db_session)], movie_id: int = Path(gt=0)):
    orm_select_statement = select(Movie).where(Movie.id == movie_id).where(Movie.owner_id == current_user.id)
    result = db.execute(orm_select_statement)
    movie_item = result.scalar_one_or_none()
    if movie_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid movie ID")
    db.delete(movie_item)
    db.commit()
