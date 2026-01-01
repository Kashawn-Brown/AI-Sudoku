from contextlib import contextmanager
from sqlalchemy.orm import Session
import json
from typing import List, Dict, Optional
from fastapi import HTTPException

@contextmanager
def db_transaction(db: Session):
    """
    Context manager for database transactions.
    Ensures all database operations within the context are atomic.
    
    Args:
        db (Session): SQLAlchemy database session
        
    Usage:
        with db_transaction(db):
            # perform database operations
            db.add(some_object)
            db.refresh(some_object)
    """
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise

class BoardStateManager:
    @staticmethod
    def validate_move(board: List[List[int]], row: int, col: int, value: int) -> bool:
        """
        Validates if a move follows Sudoku rules.

        Args:
            board (List[List[int]]): The current state of the Sudoku board.
            row (int): The row index of the move.
            col (int): The column index of the move.
            value (int): The value to be placed in the cell.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        # Check if the move is within the board boundaries and the value is valid
        if not (0 <= row < 9 and 0 <= col < 9 and 1 <= value <= 9):
            return False
            
        # Check row for conflicts
        for j in range(9):
            if j != col and board[row][j] == value:
                return False
                
        # Check column for conflicts
        for i in range(9):
            if i != row and board[i][col] == value:
                return False
                
        # Check 3x3 box for conflicts
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and board[i][j] == value:
                    return False
                    
        # If all checks pass, the move is valid
        return True

    @staticmethod
    def calculate_score(elapsed_time: int, mistakes: int, hints: int, completion: float) -> int:
        """
        Calculate game score based on performance metrics.

        Args:
            elapsed_time (int): Time taken to complete the game in seconds.
            mistakes (int): Number of mistakes made during the game.
            hints (int): Number of hints used during the game.
            completion (float): Percentage of board completion.

        Returns:
            int: The calculated score.
        """
        base_score = 10000
        time_penalty = elapsed_time // 60 * 100  # Penalty per minute
        mistake_penalty = mistakes * 500
        hint_penalty = hints * 750
        
        # Calculate score by subtracting penalties from base score
        score = base_score - time_penalty - mistake_penalty - hint_penalty
        # Adjust score based on completion percentage
        score = int(score * (completion / 100))
        # Ensure score is not negative
        return max(0, score)

    @staticmethod
    def calculate_completion(board: List[List[int]]) -> float:
        """
        Calculate board completion percentage.

        Args:
            board (List[List[int]]): The current state of the Sudoku board.

        Returns:
            float: The percentage of board completion.
        """
        # Count filled cells (non-zero values)
        filled = sum(1 for row in board for cell in row if cell != 0)
        # Calculate and return completion percentage
        return (filled / 81) * 100