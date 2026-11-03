import httpx
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from database import auth_engine, users_engine
from models import AuthUser, Friendship

router = APIRouter()

@router.get("/search")
def search_friends(query: str, current_user_id: int):
    with Session(auth_engine) as auth_session, Session(users_engine) as users_session:
        users = auth_session.exec(
            select(AuthUser).where(
                (AuthUser.id != current_user_id) & 
                ((AuthUser.email.contains(query.lower())) | (AuthUser.full_name.contains(query)))
            )
        ).all()
        
        result = []
        for u in users:
            friendship = users_session.exec(
                select(Friendship).where(
                    ((Friendship.user_id_1 == current_user_id) & (Friendship.user_id_2 == u.id)) |
                    ((Friendship.user_id_1 == u.id) & (Friendship.user_id_2 == current_user_id))
                )
            ).first()
            
            status = "none"
            if friendship:
                status = friendship.status
                if friendship.status == "pending" and friendship.user_id_1 == current_user_id:
                    status = "sent"
            
            result.append({"id": u.id, "email": u.email, "status": status})
        return result

@router.post("/request")
def send_friend_request(sender_id: int, receiver_id: int):
    with Session(users_engine) as session:
        existing = session.exec(
            select(Friendship).where(
                ((Friendship.user_id_1 == sender_id) & (Friendship.user_id_2 == receiver_id)) |
                ((Friendship.user_id_1 == receiver_id) & (Friendship.user_id_2 == sender_id))
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe una solicitud o amistad")
        
        new_req = Friendship(user_id_1=sender_id, user_id_2=receiver_id, status="pending")
        session.add(new_req)
        session.commit()
        
        try:
            with httpx.Client() as client:
                client.post(f"http://notifications-service:8004/notify?user_id={receiver_id}&type=friend_request&message=Tienes una nueva solicitud de amistad&related_id={sender_id}")
        except Exception as e:
            print(f"Error enviando notificación: {e}")

        return {"msg": "Solicitud enviada"}

@router.get("/requests/{user_id}")
def get_pending_requests(user_id: int):
    with Session(auth_engine) as auth_session, Session(users_engine) as users_session:
        requests = users_session.exec(
            select(Friendship).where(Friendship.user_id_2 == user_id, Friendship.status == "pending")
        ).all()
        result = []
        for req in requests:
            sender = auth_session.get(AuthUser, req.user_id_1)
            if sender:
                result.append({"request_id": req.id, "sender_id": sender.id, "sender_name": sender.email})
        return result

@router.post("/accept/{request_id}")
def accept_friend_request(request_id: int):
    with Session(users_engine) as session:
        req = session.get(Friendship, request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        req.status = "accepted"
        session.add(req)
        session.commit()
        return {"msg": "Amistad aceptada"}

@router.get("/list/{user_id}")
def get_friends(user_id: int):
    with Session(auth_engine) as auth_session, Session(users_engine) as users_session:
        friendships = users_session.exec(
            select(Friendship).where(
                ((Friendship.user_id_1 == user_id) | (Friendship.user_id_2 == user_id)),
                Friendship.status == "accepted"
            )
        ).all()
        
        friend_ids = []
        for f in friendships:
            friend_ids.append(f.user_id_2 if f.user_id_1 == user_id else f.user_id_1)
            
        if not friend_ids:
            return []
            
        friends = auth_session.exec(select(AuthUser).where(AuthUser.id.in_(friend_ids))).all()
        return [{"id": f.id, "email": f.email} for f in friends]