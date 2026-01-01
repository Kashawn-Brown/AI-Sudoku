from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserBase, UserCreate, UserResponse, UserStatsResponse, UserUpdate
from crud import user_crud
from models import User
from security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def root():
    return {"message": "Now in the users route"}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's profile data.
    """

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_guest=current_user.is_guest,
        created_at=current_user.created_at
    )


@router.post("/register", response_model=UserResponse)
def create_user_endpoint(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new user. 
    Currently, the database commit is commented out for testing purposes.
    """

    test_user = user_crud.create_user(db, user_data)  # Call the CRUD function
    
    # Comment out the actual database commit inside `crud.py` before testing
    return test_user


@router.get("/allusers", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """
    Retrieve all users.
    """
    return user_crud.get_users(db)


@router.get("/userid/{user_id}", response_model=UserResponse)
def read_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    return user


@router.get("/username/{username}", response_model=UserResponse)
def read_user_by_username(username: str, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with username '{username}' not found")
    return user


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user's statistics based on their user ID.
    """
    user_stats = user_crud.get_user_stats(db, user_id)
    
    if not user_stats:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_stats


@router.patch("/update/{user_id}", response_model=UserResponse)
def update_user_route(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 👈 This automatically validates the token!
):
    """
    Update a user's details based on provided data (username, email, password).

    - Will return the updated user data in response.
    - Password is hashed if provided.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail=f"Not authorized to update this user. \nWrong user id found \n{current_user.id} tyring to update {user_id}")
    
    updated_user = user_crud.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user


# NOTE: Delete route is primarily for development/testing purposes.
#       Revisit for production to decide on deletion policy.
@router.delete("/delete/{user_id}", status_code=204)
def delete_user_route(user_id: int, db: Session = Depends(get_db)):
    """
    Deletes a user by ID.
    Returns 204 No Content on success.
    """
    success = user_crud.delete_user(db, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="User not found")