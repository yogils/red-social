from fastapi import FastAPI
from database import users_engine
from models import Friendship
from sqlmodel import SQLModel
from routes import router as friends_router

app = FastAPI(title="UNAL Friends Service")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(users_engine)

app.include_router(friends_router, tags=["Friends"])