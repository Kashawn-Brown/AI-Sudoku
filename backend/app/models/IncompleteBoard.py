from sqlalchemy import Column, Integer, Text, String, Boolean, Numeric, TIMESTAMP, ForeignKey, func, Float, Interval, ARRAY
from database import Base
from sqlalchemy.orm import relationship

# IncompleteBoard Database Model
class IncompleteBoard(Base):
    """
    Represents a Sudoku board that a user started but never finished and moved on.
    """
    __tablename__ = "incomplete_boards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    completion_percentage = Column(Numeric(5,2), default=0.00)
    score = Column(Integer, default=0)