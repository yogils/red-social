from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import PyJWTError as JWTError
from passlib.context import CryptContext
from sqlmodel import Session, select
import httpx

from database import engine
from models import User, UserCreate, UserResponse, TokenResponse

router = APIRouter()

SECRET_KEY = "cambiar-en-produccion-unal-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate):
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == user_data.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=pwd_context.hash(user_data.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        try:
            with httpx.Client() as client:
                client.post("http://user-service:8002/profiles", json={
                    "id": user.id,
                    "full_name": user.full_name
                })
        except Exception as e:
            print(f"Advertencia: No se pudo crear el perfil en el User Service: {e}")
        
        return user

@router.post("/login", response_model=TokenResponse)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == form_data.username)).first()
        if not user or not pwd_context.verify(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        token = create_access_token({"sub": str(user.id), "email": user.email})
        return TokenResponse(access_token=token)

@router.get("/verify")
def verify_token(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": int(payload["sub"]), "email": payload["email"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")