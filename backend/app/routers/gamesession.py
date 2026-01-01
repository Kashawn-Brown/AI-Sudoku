from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from database import get_db
from models import GameSession
from schemas import GameSessionResponse, GameSessionCreate, GameSessionUpdate, CompletedBoardCreate, CompletedBoardResponse

from crud import gamesession_crud, completedboard_crud


router = APIRouter(prefix="/gamesession", tags=["GameSession"])

@router.get("/")
def root():
    return {"message": "Now in the Game Session route"}


@router.post("/start", response_model=GameSessionResponse)
def start_game_session(session_data: GameSessionCreate, db: Session = Depends(get_db)):
    """
    Start a new game session. If a session already exists for the user, replace it.
    """
    
    return gamesession_crud.create_game_session(db, session_data)


@router.post("/move/{session_id}", response_model=GameSessionResponse)
def make_move(
    session_id: int,
    row: int = Body(..., ge=0, lt=9),
    col: int = Body(..., ge=0, lt=9),
    value: int = Body(..., ge=1, le=9),
    db: Session = Depends(get_db)
):
    """Make a move in the current game"""
    session = gamesession_crud.get_active_game_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
        
    return gamesession_crud.update_cell_and_track_progress(
        db, session, row, col, value
    )


@router.post("/hint/{session_id}")
def get_hint(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get a hint for the current game"""
    session = gamesession_crud.get_active_game_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
        
    return gamesession_crud.get_hint(db, session)


@router.get("/active/user/{user_id}", response_model=GameSessionResponse)
def get_active_game_session(user_id: int, db: Session = Depends(get_db)):
    """
    Fetch the current active game session for a user.

    - Requires `user_id` as query param.
    - Returns the session if it exists.
    """
    session = gamesession_crud.get_active_game_session(db, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found."
        )
    
    return session


@router.patch("/update/{user_id}", response_model=GameSessionResponse)
def update_game_session(user_id: int, session_updates: GameSessionUpdate, db: Session = Depends(get_db)):
    """
    Update the game session with new progress data.
    
    Only the provided fields will be updated (partial update).
    """
    # 1. Get the active game session for the user
    session = gamesession_crud.get_active_game_session(db, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found for this user."
        )

    # 2. Update only the fields that were provided
    updated_session = gamesession_crud.update_game_session(db, session, session_updates)
    
    return updated_session

##### Do an update_cell where just the position and number is sent in and it is validated (or might just be update, and have to change thinking)
@router.patch("/update_cell/{user_id}", response_model=GameSessionResponse)
def update_cell(
    user_id: int,
    row: int = Body(..., embed=True),
    col: int = Body(..., embed=True),
    value: int = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Update a single cell in the game board.
    
    Handles logic such as:
    - Validating the move
    - Updating elapsed time and last active timestamp
    - Mistake tracking
    - Completion checking
    """
    session = gamesession_crud.get_active_game_session(db, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
    
    updated_session = gamesession_crud.update_cell_and_track_progress(
        db=db,
        session=session,
        row=row,
        col=col,
        value=value
    )

    return updated_session


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def end_game_session(user_id: int, db: Session = Depends(get_db)):
    """
    End the active game session for a user by deleting it.

    - Requires the user_id to locate the session.
    - If no session exists, return a 404 error.
    - If deletion is successful, return a 204 No Content response.
    """
    # Check if the user has an active session
    session = gamesession_crud.get_active_game_session(db, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session found to end."
        )
    
    # Delete the session
    gamesession_crud.delete_game_session(db, session)



@router.get("/allgamesessions", response_model=list[GameSessionResponse])
def get_game_sessions(db: Session = Depends(get_db)):
    """
    Retrieve all game sessions.
    """
    return gamesession_crud.get_game_sessions(db)



@router.post("/complete/{user_id}", response_model=CompletedBoardResponse)
def complete_game(user_id: int, db: Session = Depends(get_db)):
    """
    Completes a game session for the user by transferring the session data
    to the completed_boards table and deleting the game session.
    """

    # Step 1: Retrieve the active game session for the user
    game_session = gamesession_crud.get_active_game_session(db, user_id)
    if not game_session:
        raise HTTPException(status_code=404, detail="Active game session not found for this user")

    # Step 2: Prepare data for the completed board
    completed_board_data = CompletedBoardCreate(
        user_id=game_session.user_id,
        board_id=game_session.board_id,
        score=game_session.score,
        total_time_spent=game_session.total_time_spent,
        hints_used=game_session.hints_used,
        mistakes_made=game_session.mistakes_made,
    )

    # Step 3: Insert the completed board entry into the database
    completed_board = completedboard_crud.create_completed_board(db, completed_board_data)

    # Step 4: Delete the completed game session (since the game is finished)
    gamesession_crud.delete_game_session(db, game_session)

    # Step 5: Return the completed board data
    return completed_board







