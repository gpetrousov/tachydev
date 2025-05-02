from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey
from pydantic import BaseModel, Field
from typing import List


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
