from fastapi import APIRouter, HTTPException, UploadFile, File
from sqlmodel import Session
from database import engine
from models import UserProfile, UserProfileCreate
import shutil
import uuid
import os
from pydantic import BaseModel

class ProfileUpdate(BaseModel):
    career: str | None = None
    bio: str | None = None

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "user-service"}

@router.post("/profiles")
def create_profile(profile: UserProfileCreate):
    with Session(engine) as session:
        existing = session.get(UserProfile, profile.id)
        if existing:
            return existing
        new_profile = UserProfile(id=profile.id, full_name=profile.full_name)
        session.add(new_profile)
        session.commit()
        session.refresh(new_profile)
        return new_profile

@router.get("/profiles/{user_id}")
def get_profile_data(user_id: int):
    with Session(engine) as session:
        profile = session.get(UserProfile, user_id)
        if not profile:
            return {"id": user_id, "full_name": "Usuario", "profile_picture_url": None}
        return profile

@router.post("/profiles/{user_id}/picture")
def update_profile_picture(user_id: int, image_url: str):
    with Session(engine) as session:
        profile = session.get(UserProfile, user_id)
        if not profile:
            profile = UserProfile(
                id=user_id, 
                full_name=f"Usuario {user_id}", 
                profile_picture_url=image_url
            )
        else:
            profile.profile_picture_url = image_url
        
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"image_url": f"/uploads/{unique_filename}"}




@router.post("/profiles/{user_id}/update")
def update_profile(user_id: int, profile_data: ProfileUpdate):
    with Session(engine) as session:
        profile = session.get(UserProfile, user_id)
        if not profile:
            # Si no existe, lo creamos
            profile = UserProfile(id=user_id, full_name=f"Usuario {user_id}")
        
        if profile_data.career is not None:
            profile.career = profile_data.career
        if profile_data.bio is not None:
            profile.bio = profile_data.bio
            
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile