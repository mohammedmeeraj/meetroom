from jose import jwt, JWTError
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ----Password helpers-------------------------------------------
def hash_password(password) -> str:
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return password_hash.verify(plain_password, hashed_password)
