from jose import jwt, JWTError
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime, timezone
from app.dependencies import get_settings
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User

settings = get_settings()

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(db: Session, email: str, password: str) -> Optional[dict]:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Fake password check to ensure the request takes roughly the same amount of time to respond to prevent timing attacks
        verify_password(password, DUMMY_HASH)
        return False
    
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

# ----Password helpers-------------------------------------------
def hash_password(password) -> str:
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# ----JWT helpers-------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
    
