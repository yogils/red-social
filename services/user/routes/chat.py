from fastapi import APIRouter, Query, UploadFile, File
from sqlmodel import Session, select
from database import engine
from models import Message, MessageCreate
import shutil
import uuid
import os

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/messages/{user_id}")
def get_messages(user_id: int, other_id: int = Query(...)):
    with Session(engine) as session:
        messages = session.exec(
            select(Message).where(
                ((Message.sender_id == user_id) & (Message.receiver_id == other_id)) |
                ((Message.sender_id == other_id) & (Message.receiver_id == user_id))
            ).order_by(Message.created_at)
        ).all()
        return messages

@router.post("/messages")
def send_message(msg_data: MessageCreate):
    with Session(engine) as session:
        new_msg = Message(**msg_data.model_dump())
        session.add(new_msg)
        session.commit()
        session.refresh(new_msg)
        return new_msg

@router.get("/messages/unread/{user_id}")
def count_unread_messages(user_id: int):
    with Session(engine) as session:
        count = len(session.exec(select(Message).where(Message.receiver_id == user_id, Message.is_read == False)).all())
        return {"count": count}

@router.post("/messages/read/{user_id}")
def mark_messages_read(user_id: int, sender_id: int):
    with Session(engine) as session:
        unread = session.exec(select(Message).where(Message.receiver_id == user_id, Message.sender_id == sender_id, Message.is_read == False)).all()
        for m in unread:
            m.is_read = True
            session.add(m)
        session.commit()
        return {"msg": "Mensajes leídos"}

@router.post("/upload")
async def upload_chat_file(file: UploadFile = File(...)):
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_type = "image"
    if file_extension.lower() in [".mp4", ".mov", ".avi"]:
        file_type = "video"
    elif file_extension.lower() in [".mp3", ".wav", ".ogg", ".m4a"]:
        file_type = "audio"
        
    return {"file_url": f"/uploads/{unique_filename}", "file_type": file_type}