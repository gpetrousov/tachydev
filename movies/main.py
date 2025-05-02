from fastapi import FastAPI
from movies.routers import users, movies
from movies.utils import engine
from movies.models import Base


app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(users.router)
app.include_router(movies.router)
