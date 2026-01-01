from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Board
from schemas import BoardResponse, BoardUpdate

import random


router = APIRouter(prefix="/boards", tags=["Boards"])

@router.get("/")
def root():
    return {"message": "Now in the boards route"}


@router.get("/allboards", response_model=List[BoardResponse])
def get_all_boards(db: Session = Depends(get_db)):
    """
    Fetch all Sudoku boards from the database.
    """
    boards = db.query(Board).all()
    return boards

@router.get("/easy", response_model=List[BoardResponse])
def get_easy_boards(db: Session = Depends(get_db)):
    """
    Fetch all 'easy' difficulty boards.
    """
    boards = db.query(Board).filter(Board.difficulty == "easy").all()
    return boards

@router.get("/medium", response_model=List[BoardResponse])
def get_medium_boards(db: Session = Depends(get_db)):
    """
    Fetch all 'medium' difficulty boards.
    """
    boards = db.query(Board).filter(Board.difficulty == "medium").all()
    return boards

@router.get("/hard", response_model=List[BoardResponse])
def get_hard_boards(db: Session = Depends(get_db)):
    """
    Fetch all 'hard' difficulty boards.
    """
    boards = db.query(Board).filter(Board.difficulty == "hard").all()
    return boards

@router.get("/boardid/{board_id}", response_model=BoardResponse)
def get_board_by_id(board_id: int, db: Session = Depends(get_db)):
    """
    Fetch a specific board by its ID.
    Raises 404 if not found.
    """
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found.")
    
    return board

@router.get("/random", response_model=BoardResponse)
def get_random_board(db: Session = Depends(get_db)):
    """
    Return a random board from any difficulty.
    """
    boards = db.query(Board).all()
    if not boards:
        raise HTTPException(status_code=404, detail="No boards available.")
    
    return random.choice(boards)

@router.get("/random/easy", response_model=BoardResponse)
def get_random_easy_board(db: Session = Depends(get_db)):
    """
    Return a random board with difficulty 'easy'.
    """
    boards = db.query(Board).filter(Board.difficulty == "easy").all()
    if not boards:
        raise HTTPException(status_code=404, detail="No easy boards available.")
    
    return random.choice(boards)

@router.get("/random/medium", response_model=BoardResponse)
def get_random_medium_board(db: Session = Depends(get_db)):
    """
    Return a random board with difficulty 'medium'.
    """
    boards = db.query(Board).filter(Board.difficulty == "medium").all()
    if not boards:
        raise HTTPException(status_code=404, detail="No medium boards available.")
    
    return random.choice(boards)

@router.get("/random/hard", response_model=BoardResponse)
def get_random_hard_board(db: Session = Depends(get_db)):
    """
    Return a random board with difficulty 'hard'.
    """
    boards = db.query(Board).filter(Board.difficulty == "hard").all()
    if not boards:
        raise HTTPException(status_code=404, detail="No hard boards available.")
    
    return random.choice(boards)

@router.patch("/updateboard/{board_id}", response_model=BoardUpdate)
def update_board(board_id: int, update_data: BoardUpdate, db: Session = Depends(get_db)):
    """
    Update a board's stats or tags.
    Only fields provided in the request will be updated.
    """
    # Find board by its id
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Convert the incoming Pydantic model to a dictionary
    # Only include fields that were actually provided in the request
    update_fields = update_data.model_dump(exclude_unset=True)

    # Update the board object dynamically for each field
    for key, value in update_fields.items():
        setattr(board, key, value)

    # Save changes to the database
    db.commit()
    db.refresh(board)

    # Return the updated board (only includes fields from BoardUpdate schema)
    return board

@router.delete("/delete/{board_id}")
def delete_board(board_id: int, db: Session = Depends(get_db)):
    """
    Delete a board by its ID.
    """
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # db.delete(board)
    # db.commit()

    return {"message": f"Board {board_id} deleted successfully."}

# Route to get the count of easy boards
@router.get("/count/easy", response_model=int)
def get_easy_count(db: Session = Depends(get_db)):
    """
    Get the count of boards with difficulty 'easy'.
    """
    count = db.query(Board).filter(Board.difficulty == 'easy').count()
    return count

# Route to get the count of medium boards
@router.get("/count/medium", response_model=int)
def get_medium_count(db: Session = Depends(get_db)):
    """
    Get the count of boards with difficulty 'medium'.
    """
    count = db.query(Board).filter(Board.difficulty == 'medium').count()
    return count

# Route to get the count of hard boards
@router.get("/count/hard", response_model=int)
def get_hard_count(db: Session = Depends(get_db)):
    """
    Get the count of boards with difficulty 'hard'.
    """
    count = db.query(Board).filter(Board.difficulty == 'hard').count()
    return count