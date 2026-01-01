from sqlalchemy import Column, Integer, Text, String, Boolean, Numeric, TIMESTAMP, ForeignKey, func, Float, Interval, ARRAY
from database import Base
from sqlalchemy.orm import relationship

# User Database Model
class User(Base):
    """
    Represents a user in the system.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    password_hash = Column(Text)  # Securely stored password hash
    created_at = Column(TIMESTAMP, server_default=func.now())  # Account creation timestamp
    active_game_id = Column(Integer, ForeignKey("game_sessions.id", ondelete="SET NULL"), nullable=True)
    high_score = Column(Integer, default=0)
    is_guest = Column(Boolean, default=True)
    
    completed_boards_count = Column(Integer, default=0)
    incomplete_boards_count = Column(Integer, default=0)
    weekly_completed_boards_count = Column(Integer, default=0)
    completed_boards_easy = Column(Integer, default=0)
    completed_boards_medium = Column(Integer, default=0)
    completed_boards_hard = Column(Integer, default=0)
    completed_boards_expert = Column(Integer, default=0)

    total_games_played_easy = Column(Integer, default=0)
    total_games_played_medium = Column(Integer, default=0)
    total_games_played_hard = Column(Integer, default=0)
    total_games_played_expert = Column(Integer, default=0)

    win_rate_easy = Column(Numeric(5, 2), default=0.00)
    win_rate_medium = Column(Numeric(5, 2), default=0.00)
    win_rate_hard = Column(Numeric(5, 2), default=0.00)
    win_rate_expert = Column(Numeric(5, 2), default=0.00)

    completion_percentage_easy = Column(Numeric(5, 2), default=0.00)
    completion_percentage_medium = Column(Numeric(5, 2), default=0.00)
    completion_percentage_hard = Column(Numeric(5, 2), default=0.00)
    completion_percentage_expert = Column(Numeric(5, 2), default=0.00)

    fastest_completion_time_easy = Column(Interval)
    fastest_completion_time_medium = Column(Interval)
    fastest_completion_time_hard = Column(Interval)
    fastest_completion_time_expert = Column(Interval)

    average_completion_time_easy = Column(Interval)
    average_completion_time_medium = Column(Interval)
    average_completion_time_hard = Column(Interval)
    average_completion_time_expert = Column(Interval)

    streak_count = Column(Integer, default=0)

    # lets you query related models more easily
    # Specify primaryjoin to resolve ambiguity: User has active_game_id pointing to GameSession,
    # but GameSession.user_id points back to User. We want the relationship based on user_id.
    # Using primaryjoin to explicitly specify which foreign key to use
    game_session = relationship(
        "GameSession", 
        back_populates="user", 
        uselist=False,
        primaryjoin="User.id == GameSession.user_id"  # Explicitly join on user_id (not active_game_id)
    )

