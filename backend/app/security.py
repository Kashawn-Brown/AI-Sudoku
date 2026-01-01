from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import get_db
from models import User

load_dotenv()  # Load environment variables

# Password hashing context using bcrypt - (already used in user logic)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Secret key and algorithm from .env
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # if SECRET_KEY not found in .env, default-secret-key will be used
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time


# Hashes a password using bcrypt
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verifies a plain password against the hashed one
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Creates a JWT access token with user data
def create_access_token(data: dict, expiration_time_delta: Optional[timedelta] = None) -> str:  # if expiration time is not given, uses the default (30 min)
    copied_data = data.copy()  # Make a copy so we don’t mutate the original dict

    # Set token expiration time
    expire = datetime.now(timezone.utc) + (expiration_time_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    copied_data.update({"exp": expire})  # JWT standard claim

    # Encode token with SECRET_KEY and ALGORITHM
    return jwt.encode(copied_data, SECRET_KEY, algorithm=ALGORITHM)

# Verifies and decodes a JWT token
def verify_access_token(token: str) -> Optional[dict]:
    try:
        # Decode token using the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Will contain user data like {'sub': user_id or username}
    except JWTError:
        return None  # Invalid token


# OAuth2 scheme to extract token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Dependency to get the current user from the JWT token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token using the same secret and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Pull user id from token payload (adjust if you're using different key name)
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Look up user in database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user

