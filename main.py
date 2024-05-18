from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import get_db, Base, engine, init_db
from schemas import User, UserCreate, Token
from crud import get_user_by_username, create_user
from auth import authenticate_user, get_current_user, create_tokens_for_user
from subscribe import subscribe_to_topic
import asyncio

app = FastAPI()
init_db()
# Initialize the database
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    await subscribe_to_topic()

@app.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)

@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, refresh_token = create_tokens_for_user(user)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/refresh", response_model=Token)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = decode_access_token(refresh_token)
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None or user.refresh_token != refresh_token:
        raise credentials_exception
    access_token, new_refresh_token = create_tokens_for_user(user)
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
