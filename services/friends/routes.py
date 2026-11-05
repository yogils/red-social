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
            
            result.append({"id": u.id, "email": u.email, "full_name": u.full_name, "faculty": u.faculty, "status": status})
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
        
        with Session(auth_engine) as auth_session:
            sender = auth_session.get(AuthUser, sender_id)
            sender_name = sender.full_name if sender else "Alguien"

        try:
            with httpx.Client() as client:
                client.post(
                    f"http://notifications-service:8004/notify",
                    params={
                        "user_id": receiver_id,
                        "type": "friend_request",
                        "message": f"{sender_name} te ha enviado una solicitud de amistad.",
                        "related_id": sender_id
                    }
                )
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
                result.append({"request_id": req.id, "sender_id": sender.id, "sender_name": sender.full_name, "sender_email": sender.email, "sender_faculty": sender.faculty})
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
        
        sender_id = req.user_id_1
        
        try:
            with httpx.Client() as client:
                client.post(
                    f"http://notifications-service:8004/notify",
                    params={
                        "user_id": sender_id,
                        "type": "friend_accept",
                        "message": "Tu solicitud de amistad ha sido aceptada."
                    }
                )
        except Exception as e:
            print(f"Error enviando notificación de aceptación: {e}")

        return {"msg": "Amistad aceptada"}

@router.delete("/remove/{friend_id}")
def remove_friend(friend_id: int, user_id: int):
    with Session(users_engine) as session:
        friendship = session.exec(
            select(Friendship).where(
                ((Friendship.user_id_1 == user_id) & (Friendship.user_id_2 == friend_id)) |
                ((Friendship.user_id_1 == friend_id) & (Friendship.user_id_2 == user_id)),
                Friendship.status == "accepted"
            )
        ).first()
        
        if not friendship:
            raise HTTPException(status_code=404, detail="No son amigos")
        
        session.delete(friendship)
        session.commit()
        return {"msg": "Amigo eliminado"}

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
        return [{"id": f.id, "email": f.email, "full_name": f.full_name, "faculty": f.faculty} for f in friends]

@router.get("/suggestions/{user_id}")
def get_friend_suggestions(user_id: int):
    with Session(users_engine) as session:
        my_friendships = session.exec(
            select(Friendship).where(
                ((Friendship.user_id_1 == user_id) | (Friendship.user_id_2 == user_id)),
                Friendship.status == "accepted"
            )
        ).all()
        
        my_friend_ids = set()
        for f in my_friendships:
            my_friend_ids.add(f.user_id_2 if f.user_id_1 == user_id else f.user_id_1)
        
        if not my_friend_ids:
            return []

        suggestions = {}
        for friend_id in my_friend_ids:
            friends_of_friend = session.exec(
                select(Friendship).where(
                    ((Friendship.user_id_1 == friend_id) | (Friendship.user_id_2 == friend_id)),
                    Friendship.status == "accepted"
                )
            ).all()
            
            for fof in friends_of_friend:
                candidate_id = fof.user_id_2 if fof.user_id_1 == friend_id else fof.user_id_1
                if candidate_id != user_id and candidate_id not in my_friend_ids:
                    suggestions[candidate_id] = suggestions.get(candidate_id, 0) + 1
        
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        with Session(auth_engine) as auth_session:
            result = []
            for cand_id, mutual_count in sorted_suggestions:
                user_data = auth_session.get(AuthUser, cand_id)
                if user_data:
                    result.append({
                        "id": user_data.id,
                        "full_name": user_data.full_name,
                        "email": user_data.email,
                        "faculty": user_data.faculty,
                        "mutual_friends": mutual_count
                    })
            return result