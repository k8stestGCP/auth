from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import timedelta
from database import get_db
from models import User
from security import verify_password, create_access_token, create_refresh_token, decode_access_token
from schemas import TokenData
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(token: str):
    db = SessionLocal()

    username = decode_access_token(token)
    if username is None:
        return None
    user = db.query(User).filter(User.username == username).first()

    return user

def create_tokens_for_user(user: User):
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    refresh_token_expires = timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")))
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "id": user.id}, expires_delta=refresh_token_expires
    )
    user.refresh_token = refresh_token
    return access_token, refresh_token
