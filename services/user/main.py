from fastapi import FastAPI
from database import create_db_and_tables
from routes import posts, chat, profiles, comments

app = FastAPI(title="UNAL User Service")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(profiles.router, tags=["Profiles"])
app.include_router(posts.router, tags=["Posts"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(comments.router, tags=["Comments"])