from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status, Path
from typing import Annotated, Optional
from pydantic import BaseModel, Field


# DB stuff
DB_URL = "sqlite:///./todos.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


# Models
class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)


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

# Onliner dependency declaration
db_dependency = Annotated[Session, Depends(get_db_session)]


# CREATE
@app.post("/create/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_req: TodosRequest):
    new_todo = Todos(**todo_req.model_dump())
    db.add(new_todo)
    db.commit()


# READ
@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/read/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    return todo_model


# UPDATE
@app.put("/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_req: TodosRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo item not found")
    todo_model.title = todo_req.title
    todo_model.description = todo_req.description
    todo_model.priority = todo_req.priority
    todo_model.complete = todo_req.complete

    db.add(todo_model)
    db.commit()


# DELETE
@app.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo item with ID: {todo_id} not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
