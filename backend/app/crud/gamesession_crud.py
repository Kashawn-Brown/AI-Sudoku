from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session
from models import GameSession, Board
from schemas import GameSessionCreate, GameSessionUpdate
from fastapi import HTTPException
from utils import db_transaction


def create_game_session(db: Session, game_session: GameSessionCreate):
    """
    Start a new game session for the user.
    Deletes any existing active session for the user before creating the new one.
    """
    with db_transaction(db):

        # Delete any existing game session for the user
        existing_session = db.query(GameSession).filter(GameSession.user_id == game_session.user_id).first()
        if existing_session:  # need to add functionality to add to uncompleted boards
            db.delete(existing_session)

        # Get the board to start with initial state
        board = db.query(Board).filter(Board.id == game_session.board_id).first()
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")

        # Create the new game session
        new_session = GameSession(
            user_id=game_session.user_id,
            board_id=game_session.board_id,
            board_progress=board.puzzle,  # Start with the initial state
        )

        # Add new game session to database
        db.add(new_session)
        db.refresh(new_session)

        return new_session



def get_active_game_session(db: Session, user_id: int):
    """
    Get the active game session for a user.
    Returns None if no active session exists for the user.
    """
    game_session = db.query(GameSession).filter(GameSession.user_id == user_id).first()

    return game_session


def update_game_session(db: Session, session: GameSession, updates: GameSessionUpdate):
    """
    Update fields on an active game session using provided values only.
    """
    # Loop through each field in the schema
    update_data = updates.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(session, field, value)  # Dynamically update field on the model

    # Manually update the 'last_active_at' timestamp to now
    session.last_active_at = datetime.now(timezone.utc)

    # Commit changes to database
    db.commit()
    db.refresh(session)

    return session


def update_cell_and_track_progress(db: Session, session: GameSession, row: int, col: int, value: int):
    """
    Updates a single cell in the board and performs all related tracking:
    - Elapsed time
    - Mistakes
    - Completion percentage
    - Last active time
    """
    with db_transaction(db):

        # Get current board state and solution
        current_board = json.loads(session.board_progress)
        board = db.query(Board).filter(Board.id == session.board_id).first()
        solution = json.loads(board.solution)

        # Validate move
        if not BoardStateManager.validate_move(current_board, row, col, value):
            raise HTTPException(
                status_code=400, 
                detail="Invalid move: violates Sudoku rules"
            )

        # Time tracking
        now = datetime.now(timezone.utc)
        delta = (now - session.last_active_at).total_seconds()
        session.elapsed_time += int(delta)
        session.last_active_at = now

        # Mistake detection
        if value != solution[row][col]:
            session.mistakes_made += 1

        # Update cell and track mistakes
        if value != solution[row][col]:
            session.mistakes_made += 1
        current_board[row][col] = value
        session.board_progress = json.dumps(current_board)

        # Update completion and score
        session.completion_percentage = BoardStateManager.calculate_completion(current_board)
        session.current_score = BoardStateManager.calculate_score(
            session.elapsed_time,
            session.mistakes_made,
            session.hints_used,
            session.completion_percentage
        )

        # Commit updates
        db.refresh(session)

    return session

def get_hint(db: Session, session: GameSession) -> dict:
    """Provides a hint for the current game state"""
    with db_transaction(db):
        board = db.query(Board).filter(Board.id == session.board_id).first()
        solution = json.loads(board.solution)
        current = json.loads(session.board_progress)

        # Find first empty cell that can be revealed
        for i in range(9):
            for j in range(9):
                if current[i][j] == 0:
                    session.hints_used += 1
                    # Update score after using hint
                    session.current_score = BoardStateManager.calculate_score(
                        session.elapsed_time,
                        session.mistakes_made,
                        session.hints_used,
                        session.completion_percentage
                    )
                    return {"row": i, "col": j, "value": solution[i][j]}

        raise HTTPException(status_code=400, detail="No hints available - board is full")


def delete_game_session(db: Session, session: GameSession):
    """
    Deletes the given game session from the database.
    """
    db.delete(session)
    db.commit()

    
def get_game_sessions(db: Session):
    """
    Fetches all game sessions from the database.
    """
    return db.query(GameSession).all()
    # return db.query(GameSession).order_by(GameSession.started_at.desc()).all()  # to return sorted by most recent session



