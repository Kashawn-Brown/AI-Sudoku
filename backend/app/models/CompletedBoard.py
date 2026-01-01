from sqlalchemy import Column, Integer, Text, String, Boolean, Numeric, TIMESTAMP, ForeignKey, func, Float, Interval, ARRAY
from database import Base
from sqlalchemy.orm import relationship

# Completed Board Database Model
class CompletedBoard(Base):
    """
    Represents a Sudoku board that has been completed by a user.
    """
    __tablename__ = "completed_boards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    completed_at = Column(TIMESTAMP, server_default=func.now())  # Timestamp of completion
    total_time_spent = Column(Integer, nullable=False)
    hints_used = Column(Integer, nullable=False, default=0)
    mistakes_made = Column(Integer, nullable=False, default=0)