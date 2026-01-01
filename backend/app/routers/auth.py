from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models import User
from schemas import UserLogin, Token
from database import get_db
from security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


# Login endpoint
@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT token if valid.

    - Checks if the username/email exists.
    - Verifies the password.
    - Returns a signed JWT access token on success.
    """
    
    # Check if user exists
    # user = db.query(User).filter((User.username == user_credentials.login) | (User.email == user_credentials.login)).first()

    user = db.query(User).filter(
        or_(
            User.username == user_credentials.login,
            User.email == user_credentials.login
        )
    ).first()
    
    # If no user found, raise specific error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or email",  # Specific about login failure
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If user exists but password is wrong
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",  # Specific about password failure
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT payload (you can include more fields if needed)
    data = {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }
    access_token = create_access_token(data=data)  # "sub" = subject

    return {"access_token": access_token, "token_type": "bearer"}