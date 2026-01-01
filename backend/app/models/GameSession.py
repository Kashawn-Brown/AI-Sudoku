from sqlalchemy import Column, Integer, Text, String, Boolean, Numeric, TIMESTAMP, ForeignKey, func, Float, Interval, ARRAY
from database import Base
from sqlalchemy.orm import relationship

# Game Session Database Model
class GameSession(Base):
    """
    Represents an active game session for a user.
    """
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    
    board_progress = Column(Text, nullable=False) 
    completion_percentage = Column(Numeric(5,2), default=0.00)
    current_score = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    mistakes_made = Column(Integer, default=0)
 
    started_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    last_active_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    elapsed_time = Column(Integer, default=0)
    
    # lets you query related models more easily
    # Specify foreign_keys to resolve ambiguity between User.active_game_id and GameSession.user_id
    # We want the relationship based on GameSession.user_id -> User.id
    user = relationship(
        "User", 
        back_populates="game_session",
        foreign_keys=[user_id]  # Use this model's user_id column as the foreign key
    )
    board = relationship("Board")

    # ADD
    # Add solution field to GameSession to avoid repeated database lookups
    # Add initial_board field to track the starting state
    # Add is_paused boolean field for proper time tracking
    # Add remaining_hints field to limit hints per game