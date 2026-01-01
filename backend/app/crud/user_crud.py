from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User
from schemas import UserCreate, UserResponse, UserStatsResponse, UserUpdate
import random
import string
from typing import Optional
from fastapi import HTTPException
from security import verify_password, create_access_token
from utils import db_transaction


# =========================
# USER 
# =========================

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Creates a new User
def create_user(db: Session, user_data: UserCreate) -> UserResponse:
    """
    Creates a new user. Supports both registered users and guests.

    - If `is_guest=True`, a random guest username is generated.
    - If an email and password are provided, the password is hashed before storing.
    - Ensures username uniqueness.

    Args:
        db (Session): The database session.
        user_data (UserCreate): The user data containing username, email, password, and guest status.

    Returns:
        UserResponse: The newly created user.
    """
    with db_transaction(db):

        # Generate a guest username if no username is provided
        if user_data.is_guest:
            while True:
                random_username = "Guest_" + "".join(random.choices(string.ascii_letters + string.digits, k=6))
                existing_user = db.query(User).filter(User.username == random_username).first()
                if not existing_user:
                    user_data.username = random_username
                    break
        else:
            # Check if username already exists
            existing_username = db.query(User).filter(User.username == user_data.username).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="Username already taken.")
            
            # Check if email already exists
            existing_email = db.query(User).filter(User.email == user_data.email).first()
            print(existing_email)
            if existing_email and existing_email != None:
                raise HTTPException(status_code=400, detail="Email already taken.")
        
        # Hash password if provided
        hashed_password = None
        if user_data.password:
            hashed_password = pwd_context.hash(user_data.password)

        # Create new user object
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            is_guest=user_data.is_guest
        )

        # Add user to the database
        db.add(new_user)
        db.refresh(new_user)

    # Create JWT payload (you can include more fields if needed)
    access_token = create_access_token(data={"sub": {new_user.id, new_user.username, new_user.email, new_user.created_at}})  # "sub" = subject

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        is_guest=new_user.is_guest,
        created_at=new_user.created_at
    )

# Fetches all Users from the database
def get_users(db: Session):
    return db.query(User).all()
    """
    # Fetching all Users but with pagination
    # def get_users(db: Session, skip: int = 0, limit: int = 10):
        # return db.query(User).offset(skip).limit(limit).all()
    """

# Fetches User based on their id
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Fetches User based on their Username
def get_user_by_username(db: Session, username: str):
    # return db.query(User).filter(User.username == username).first()
    return db.query(User).filter(User.username.ilike(username)).first()
    """
    Can add support to be case insensitive

    PostgreSQL has a ILIKE operator for case-insensitive matching:
    return db.query(User).filter(User.username.ilike(username)).first()

    If you're using a database that doesn't support ILIKE, you can force lowercase:
    return db.query(User).filter(func.lower(User.username) == username.lower()).first()
    """

# Gets the stats of a user
def get_user_stats(db: Session, user_id: int) -> Optional[UserStatsResponse]:
    """Retrieve the statistics for a given user."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None  # The route will handle this case
    
    return UserStatsResponse(
        completed_boards_count=user.completed_boards_count,
        incomplete_boards_count=user.incomplete_boards_count,
        weekly_completed_boards_count=user.weekly_completed_boards_count,
        completed_boards_easy=user.completed_boards_easy,
        completed_boards_medium=user.completed_boards_medium,
        completed_boards_hard=user.completed_boards_hard,
        completed_boards_expert=user.completed_boards_expert,
        
        total_games_played_easy=user.total_games_played_easy,
        total_games_played_medium=user.total_games_played_medium,
        total_games_played_hard=user.total_games_played_hard,
        total_games_played_expert=user.total_games_played_expert,

        win_rate_easy=user.win_rate_easy,
        win_rate_medium=user.win_rate_medium,
        win_rate_hard=user.win_rate_hard,
        win_rate_expert=user.win_rate_expert,

        completion_percentage_easy=user.completion_percentage_easy,
        completion_percentage_medium=user.completion_percentage_medium,
        completion_percentage_hard=user.completion_percentage_hard,
        completion_percentage_expert=user.completion_percentage_expert,

        fastest_completion_time_easy=str(user.fastest_completion_time_easy) if user.fastest_completion_time_easy else None,
        fastest_completion_time_medium=str(user.fastest_completion_time_medium) if user.fastest_completion_time_medium else None,
        fastest_completion_time_hard=str(user.fastest_completion_time_hard) if user.fastest_completion_time_hard else None,
        fastest_completion_time_expert=str(user.fastest_completion_time_expert) if user.fastest_completion_time_expert else None,

        average_completion_time_easy=str(user.average_completion_time_easy) if user.average_completion_time_easy else None,
        average_completion_time_medium=str(user.average_completion_time_medium) if user.average_completion_time_medium else None,
        average_completion_time_hard=str(user.average_completion_time_hard) if user.average_completion_time_hard else None,
        average_completion_time_expert=str(user.average_completion_time_expert) if user.average_completion_time_expert else None,

        streak_count=user.streak_count
    )

# Updates user details based on provided user data
def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
    """
    Updates the user details based on the provided user_data.

    - Hashes the password if it is updated.
    - Updates only the provided fields (username, email, password).

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to update.
        user_data (UserUpdate): The data to update.

    Returns:
        UserResponse: The updated user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    print(user_update)

    if not user:
        return None  # User doesn't exist, handle this in the route
    
    # Guest transition to full account logic
    if user.is_guest:
        if not (user_update.email and user_update.password):
            raise HTTPException(status_code=400, detail="Guests must provide email and password to update.")

        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user_update.username).first()
        if existing_username and existing_username.id != user_id:
            raise HTTPException(status_code=400, detail="Username already taken.")
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user_update.email).first()
        if existing_email and existing_email.id != user_id:
            raise HTTPException(status_code=400, detail="Email already taken.")
        
        # Update the Guests fields (change username if a new one has been provided)
        if user_update.username:
            user.username = user_update.username
        user.email = user_update.email
        user.password_hash = pwd_context.hash(user_update.password)
        user.is_guest = False
        
    else:
        # Block email changes for registered users
        if user_update.email:
            raise HTTPException(status_code=400, detail="Registered users cannot change their email.")
    
        # Allow username and password updates if provided
        if user_update.username:
            user.username = user_update.username
        if user_update.password:
            user.password_hash = pwd_context.hash(user_update.password)

    # Commit the changes to the database
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_guest=user.is_guest,
        created_at=user.created_at
    )

# Deletes a user by ID
def delete_user(db: Session, user_id: int) -> bool:
    """
    Deletes a user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to delete.

    Returns:
        bool: True if deleted, False if user not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True



