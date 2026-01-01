from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import random

# Import database session dependency and models
from database import get_db
from models import Board
from schemas import BoardResponse

# Create a router for game-related endpoints with a prefix and tag for API docs
router = APIRouter(prefix="/game", tags=["Game"])

@router.get("/")
def get_new_game(difficulty: str = "random", db: Session = Depends(get_db)):
    """
    Retrieve a new playable Sudoku game.
    
    Args:
        difficulty: The difficulty level ('easy', 'medium', 'hard', or 'random')
        db: Database session (injected by FastAPI)
    
    Returns:
        A dictionary containing:
        - puzzle: 9x9 grid of the initial puzzle (0 = empty cell)
        - solution: 9x9 grid of the complete solution
        - difficulty: The difficulty level of the puzzle
        - board_id: The database ID of the board
    """
    # Fetch a board based on difficulty preference
    if difficulty == "random":
        # Get all boards and pick one randomly
        boards = db.query(Board).all()
        if not boards:
            raise HTTPException(status_code=404, detail="No boards available in database")
        board = random.choice(boards)
    else:
        # Filter by specific difficulty
        boards = db.query(Board).filter(Board.difficulty == difficulty.lower()).all()
        if not boards:
            raise HTTPException(
                status_code=404, 
                detail=f"No {difficulty} boards available. Try 'random' or populate the database."
            )
        board = random.choice(boards)
    
    # Parse the puzzle and solution from JSON strings stored in database
    # The database stores them as JSON strings, so we need to parse them
    try:
        puzzle = json.loads(board.puzzle)
        solution = json.loads(board.solution)
    except json.JSONDecodeError:
        # If parsing fails, raise an error
        raise HTTPException(
            status_code=500, 
            detail="Error parsing board data from database"
        )
    
    # Return the game data in a format the frontend can use
    return {
        "puzzle": puzzle,      # 9x9 grid with 0s for empty cells
        "solution": solution,  # 9x9 grid with complete solution
        "difficulty": board.difficulty,
        "board_id": board.id
    }

@router.post("/new")
def create_game():
    """Create a new Sudoku game."""
    return {"message": "New Sudoku game created"}
