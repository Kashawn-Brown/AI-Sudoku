from sqlalchemy.orm import Session
from models import CompletedBoard
from schemas import CompletedBoardCreate





def create_completed_board(db: Session, completed_board_data: CompletedBoardCreate):
    """
    Creates a CompletedBoard entry from the given data.
    """
    completed_board = CompletedBoard(**completed_board_data.model_dump())
    
    db.add(completed_board)
    db.commit()
    db.refresh(completed_board)
    
    return completed_board
