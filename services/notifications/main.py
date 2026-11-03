from fastapi import FastAPI
from database import create_db_and_tables
from routes import router as notifications_router

app = FastAPI(title="UNAL Notifications Service")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(notifications_router, tags=["Notifications"])