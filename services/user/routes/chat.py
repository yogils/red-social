import httpx
from fastapi import APIRouter, Query
from sqlmodel import Session, select
from database import engine
from models import Message, MessageCreate

router = APIRouter()

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
        
        try:
            with httpx.Client() as client:
                client.post(f"http://notifications-service:8004/notify?user_id={msg_data.receiver_id}&type=message&message=Has recibido un nuevo mensaje")
        except Exception as e:
            print(f"Error enviando notificación: {e}")

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