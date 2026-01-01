from sqlalchemy import Column, Integer, Text, String, Boolean, Numeric, TIMESTAMP, ForeignKey, func, Float, Interval, ARRAY
from database import Base
from sqlalchemy.orm import relationship

# Board Database Model
class Board(Base):
    """
    Represents a Sudoku board in the database.
    """
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    puzzle = Column(Text, nullable=False)  # Stores the board as a string (e.g., comma-separated or JSON)
    solution = Column(Text, nullable=False)  # Stores the solution as a string
    difficulty = Column(String(10), nullable=False, default="unknown")  # Difficulty level (easy, medium, hard, expert)
    created_at = Column(TIMESTAMP, server_default=func.now())  # Auto timestamp

    completion_rate = Column(Numeric(5, 2), default=0.00)  # Track success rate 
    average_completion_time = Column(Numeric(5, 2))  
    fastest_time = Column(Integer)  # Time in seconds (integer)
    times_played = Column(Integer, default=0)
    times_completed = Column(Integer, default=0)
    tags = Column(ARRAY(String))  # Requires PostgreSQL

    #  lets you query related models more easily
    sessions = relationship("GameSession", back_populates="board")