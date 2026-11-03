from fastapi import FastAPI
from database import create_db_and_tables
from routes import router as auth_router

app = FastAPI(title="UNAL Auth Service")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth_router, tags=["Auth"])