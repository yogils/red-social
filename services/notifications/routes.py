from fastapi import APIRouter
from sqlmodel import Session, select
from database import engine
from models import Notification

router = APIRouter()

@router.post("/notify")
def create_notification(user_id: int, type: str, message: str, related_id: int = None):
    with Session(engine) as session:
        notif = Notification(user_id=user_id, type=type, message=message, related_id=related_id)
        session.add(notif)
        session.commit()
        return {"msg": "Notificación creada"}

@router.get("/{user_id}")
def get_notifications(user_id: int):
    with Session(engine) as session:
        notifs = session.exec(
            select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
        ).all()
        return notifs

@router.post("/{user_id}/read")
def mark_all_read(user_id: int):
    with Session(engine) as session:
        notifs = session.exec(select(Notification).where(Notification.user_id == user_id, Notification.is_read == False)).all()
        for n in notifs:
            n.is_read = True
            session.add(n)
        session.commit()
        return {"msg": "Notificaciones leídas"}

@router.get("/unread/{user_id}")
def count_unread(user_id: int):
    with Session(engine) as session:
        count = len(session.exec(select(Notification).where(Notification.user_id == user_id, Notification.is_read == False)).all())
        return {"count": count}