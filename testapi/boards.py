from fastapi import APIRouter

# Create a router for board-related endpoints with a prefix and tag for API docs
router = APIRouter(prefix="/board", tags=["Board"])

@router.get("/")
def get_games():
    """Retrieve a list of Sudoku games."""
    return {"message": "List of Sudoku games"}

@router.post("/new")
def create_game():
    """Create a new Sudoku game."""
    return {"message": "New Sudoku game created"}