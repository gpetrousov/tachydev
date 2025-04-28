from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, insert, select
from fastapi import FastAPI, Depends, HTTPException, status, Path
from typing import Annotated, Optional
from pydantic import BaseModel, Field


# DB stuff
DB_URL = "sqlite:///./todos.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Models
class Base(DeclarativeBase):
    pass


class Todos(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    priority: Mapped[int] = mapped_column(Integer)
    complete: Mapped[bool] = mapped_column(Boolean, default=False)


class TodosRequest(BaseModel):
    id: Optional[int] = Field(default=None, description="Optional field;Incremental ID number")
    title: str = Field(min_length=3)
    description: str = Field(min_length=4)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)

    model_config = {
            "json_schema_extra": {
                "example": {
                    "title": "New task",
                    "description": "Step 1, Step 2, Steap 3, ...",
                    "priority": 3,
                    "complete": False
                    }
                }
            }


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
Base.metadata.create_all(bind=engine)

# Onliner dependency declaration
db_dependency = Annotated[Session, Depends(get_db_session)]


# CREATE
@app.post("/create/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_req: TodosRequest):
    # new_todo = Todos(**todo_req.model_dump())
    orm_insert_statement = insert(Todos).values(**todo_req.model_dump())
    db.execute(orm_insert_statement)
    db.commit()


# READ
@app.get("/")
async def read_all(db: db_dependency):
    orm_select_statement = select(Todos)
    result = db.execute(orm_select_statement)
    return result.scalars().all()


@app.get("/read/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
    orm_select_where_statement = select(Todos).where(Todos.id == todo_id)
    result = db.execute(orm_select_where_statement)
    todo_item = result.scalar_one_or_none()
    if todo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    return todo_item


# UPDATE
@app.put("/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_req: TodosRequest, todo_id: int = Path(gt=0)):
    orm_select_statement = select(Todos).where(Todos.id == todo_id)
    todo_item = db.execute(orm_select_statement).scalar_one_or_none()
    if todo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")

    todo_item.title = todo_req.title
    todo_item.description = todo_req.description
    todo_item.priority = todo_req.priority
    todo_item.complete = todo_req.complete

    db.commit()


# DELETE
@app.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    orm_select_statement = select(Todos).where(Todos.id == todo_id)
    todo_item = db.execute(orm_select_statement).scalar_one_or_none()
    if todo_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo item with ID: {todo_id} not found")
    db.delete(todo_item)
    db.commit()
