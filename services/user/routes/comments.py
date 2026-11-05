import httpx
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from database import engine
from models import Comment, CommentCreate, Post

router = APIRouter()

@router.get("/posts/{post_id}/comments")
def get_comments(post_id: int):
    with Session(engine) as session:
        comments = session.exec(
            select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.asc())
        ).all()
        return comments

@router.post("/posts/{post_id}/comments")
def create_comment(post_id: int, comment_data: CommentCreate):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")

        new_comment = Comment(post_id=post_id, **comment_data.model_dump())
        session.add(new_comment)
        session.commit()
        session.refresh(new_comment)

        if post.author_id != comment_data.author_id:
            try:
                with httpx.Client() as client:
                    client.post(
                        f"http://notifications-service:8004/notify",
                        params={
                            "user_id": post.author_id,
                            "type": "new_comment",
                            "message": f"{comment_data.author_name} ha comentado en tu publicación.",
                            "related_id": comment_data.author_id
                        }
                    )
            except Exception as e:
                print(f"Error enviando notificación de comentario: {e}")

        return new_comment