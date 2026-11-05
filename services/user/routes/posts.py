import httpx
from fastapi import APIRouter, Query, HTTPException
from sqlmodel import Session, select
from database import engine
from models import Post, Reaction, PostCreate, ReactionCreate, Comment

router = APIRouter()

@router.get("/posts")
def get_posts(user_id: int = Query(None), only_friends: bool = Query(False)):
    allowed_authors = None
    
    if only_friends and user_id:
        try:
            with httpx.Client() as client:
                res_friends = client.get(f"http://friends-service:8003/list/{user_id}")
                if res_friends.status_code == 200:
                    friends = res_friends.json()
                    allowed_authors = [f['id'] for f in friends]
                    allowed_authors.append(user_id)
                else:
                    allowed_authors = [user_id]
        except Exception as e:
            print(f"Error obteniendo amigos para el feed: {e}")
            allowed_authors = [user_id]

    with Session(engine) as session:
        query = select(Post).where(Post.reports < 3).order_by(Post.created_at.desc())
        
        if allowed_authors is not None:
            query = query.where(Post.author_id.in_(allowed_authors))
            
        posts = session.exec(query).all()
        
        result = []
        for post in posts:
            likes = len(session.exec(select(Reaction).where(Reaction.post_id == post.id, Reaction.reaction_type == "like")).all())
            dislikes = len(session.exec(select(Reaction).where(Reaction.post_id == post.id, Reaction.reaction_type == "dislike")).all())
            comments_count = len(session.exec(select(Comment).where(Comment.post_id == post.id)).all())
            user_reaction = None
            if user_id:
                reaction = session.exec(select(Reaction).where(Reaction.post_id == post.id, Reaction.user_id == user_id)).first()
                if reaction: user_reaction = reaction.reaction_type
            result.append({**post.model_dump(), "likes_count": likes, "dislikes_count": dislikes, "user_reaction": user_reaction, "comments_count": comments_count})
        return result


@router.post("/posts")
def create_post(post_data: PostCreate):
    with Session(engine) as session:
        new_post = Post(**post_data.model_dump())
        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        
        try:
            with httpx.Client() as client:
                res_friends = client.get(f"http://friends-service:8003/list/{post_data.author_id}")
                if res_friends.status_code == 200:
                    friends = res_friends.json()
                    for friend in friends:
                        client.post(
                            f"http://notifications-service:8004/notify",
                            params={
                                "user_id": friend['id'],
                                "type": "new_post",
                                "message": f"Tu amigo {post_data.author_name} ha publicado algo nuevo."
                            }
                        )
        except Exception as e:
            print(f"Error enviando notificaciones de post: {e}")

        return new_post

@router.post("/posts/{post_id}/react")
def react_to_post(post_id: int, user_id: int, reaction_data: ReactionCreate):
    with Session(engine) as session:
        existing = session.exec(select(Reaction).where(Reaction.post_id == post_id, Reaction.user_id == user_id)).first()
        if existing:
            if existing.reaction_type == reaction_data.reaction_type:
                session.delete(existing)
            else:
                existing.reaction_type = reaction_data.reaction_type
                session.add(existing)
        else:
            session.add(Reaction(post_id=post_id, user_id=user_id, reaction_type=reaction_data.reaction_type))
        session.commit()
        likes = len(session.exec(select(Reaction).where(Reaction.post_id == post_id, Reaction.reaction_type == "like")).all())
        dislikes = len(session.exec(select(Reaction).where(Reaction.post_id == post_id, Reaction.reaction_type == "dislike")).all())
        return {"likes_count": likes, "dislikes_count": dislikes}

@router.post("/posts/{post_id}/report")
def report_post(post_id: int):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        post.reports += 1
        session.add(post)
        session.commit()
        return {"msg": "Reportado", "reports": post.reports}

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, user_id: int):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        if post.author_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este post")
        
        session.delete(post)
        session.commit()
        return {"msg": "Post eliminado"}