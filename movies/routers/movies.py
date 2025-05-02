from fastapi import APIRouter, Depends, Path
from typing import Annotated
from sqlalchemy import insert, select
from sqlalchemy.orm import Session
from starlette import status
from movies.utils import get_db_session, get_user_from_db, bcrypt_context, authenticate_user, ALGORITHM, SECRET_KEY, get_current_user
from movies.models import Movie, MovieRequest, User
from fastapi.exceptions import HTTPException


router = APIRouter(prefix="/movies", tags=["movies"])


# Get my movies
@router.get("/")
async def get_my_movies(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db_session)]):
    orm_select_statement = select(Movie).where(Movie.owner_id == current_user.id)
    result = db.execute(orm_select_statement)
    return result.scalars().all()


# Create new movie
@router.post("/add", status_code=status.HTTP_201_CREATED)
async def create_movie(current_user: Annotated[User, Depends(get_current_user)], new_movie: MovieRequest, db: Annotated[Session, Depends(get_db_session)]):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fobridden")

    insert_orm_statement = insert(Movie).values(
            **new_movie.model_dump(),
            owner_id=current_user.id
            )
    db.execute(insert_orm_statement)
    db.commit()


# Get my movie by ID
@router.get("/{movie_id}")
async def get_movie_by_id(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db_session)], movie_id: int = Path()):
    orm_select_statement = select(Movie).where(Movie.owner_id == current_user.id).where(Movie.id == movie_id)
    result = db.execute(orm_select_statement)
    movie_item = result.scalar_one_or_none()
    return movie_item


# Update my movie by ID
@router.put("/update/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
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
@router.delete("/delete/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie_by_id(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db_session)], movie_id: int = Path(gt=0)):
    orm_select_statement = select(Movie).where(Movie.id == movie_id).where(Movie.owner_id == current_user.id)
    result = db.execute(orm_select_statement)
    movie_item = result.scalar_one_or_none()
    if movie_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid movie ID")
    db.delete(movie_item)
    db.commit()
