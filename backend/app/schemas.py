from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Annotated
from datetime import datetime
from decimal import Decimal

"""
Base schemas contain shared fields.

Create schemas define required fields for creating records.

Response schemas control what is returned from the API.
"""


# =========================
# USER SCHEMAS
# =========================
class UserBase(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None  # Guests don't require emails
    is_guest: bool = Field(default=True)  # Default to guest

class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=7)  # Password is optional but must be 6+ chars if given # Guests don't require passwords

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # Password is optional for updating


# =========================
# AUTHORIZATION SCHEMAS
# =========================

class UserLogin(BaseModel):
    login: str  # Can be Users email or username
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str  # typically 'bearer'


# =========================
# USER STATS SCHEMA
# =========================

class UserStatsResponse(BaseModel):
    # Total boards completed and attempted
    completed_boards_count: int
    incomplete_boards_count: int
    weekly_completed_boards_count: int
    completed_boards_easy: int
    completed_boards_medium: int
    completed_boards_hard: int
    completed_boards_expert: int

    total_games_played_easy: int
    total_games_played_medium: int
    total_games_played_hard: int
    total_games_played_expert: int

    # Completion percentages and win rates
    win_rate_easy: Decimal = Field(default=0.00)
    win_rate_medium: Decimal = Field(default=0.00)
    win_rate_hard: Decimal = Field(default=0.00)
    win_rate_expert: Decimal = Field(default=0.00)
    
    completion_percentage_easy: Decimal = Field(default=0.00)
    completion_percentage_medium: Decimal = Field(default=0.00)
    completion_percentage_hard: Decimal = Field(default=0.00)
    completion_percentage_expert: Decimal = Field(default=0.00)
    
    # Fastest completion times (we'll use string for Interval)
    fastest_completion_time_easy: Optional[str] = None
    fastest_completion_time_medium: Optional[str] = None
    fastest_completion_time_hard: Optional[str] = None
    fastest_completion_time_expert: Optional[str] = None
    
    # Average completion times (using string as Interval)
    average_completion_time_easy: Optional[str] = None
    average_completion_time_medium: Optional[str] = None
    average_completion_time_hard: Optional[str] = None
    average_completion_time_expert: Optional[str] = None

    streak_count: int = 0

    class Config:
        from_attributes = True


# =========================
# BOARD SCHEMAS
# =========================
class BoardBase(BaseModel):
    puzzle: str
    solution: str
    difficulty: str = Field(..., pattern="^(easy|medium|hard|expert)$")

class BoardCreate(BoardBase):
    pass  # Same as BoardBase

class BoardResponse(BoardBase):
    id: int
    created_at: datetime

    completion_rate: Decimal = Decimal("0.00")
    average_completion_time: Optional[Decimal] = None
    fastest_time: Optional[int] = None
    times_played: int = 0
    times_completed: int = 0
    tags: Optional[List[str]] = None

    class Config:
        from_attributes = True
        """
        bridges the gap between ORM objects and Pydantic validation
        allows Pydantic to convert ORM objects (like SQLAlchemy models) into Pydantic models
        tells Pydantic to treat ORM objects like dictionaries:
            Instead of data["id"], it can access data.id
            Instead of data["created_at"], it can access data.created_at
        """

class BoardUpdate(BaseModel):
    # All fields optional for flexibility
    completion_rate: Optional[Decimal] = None
    average_completion_time: Optional[Decimal] = None
    fastest_time: Optional[int] = None
    times_played: Optional[int] = None
    times_completed: Optional[int] = None
    tags: Optional[List[str]] = None

# =========================
# COMPLETED BOARD SCHEMAS
# =========================
class CompletedBoardBase(BaseModel):
    user_id: int
    board_id: int
    score: int = Field(..., ge=0)
    total_time_spent: int = Field(..., ge=0)
    hints_used: int = Field(..., ge=0)
    mistakes_made: int = Field(..., ge=0)

class CompletedBoardCreate(CompletedBoardBase):
    pass

class CompletedBoardResponse(CompletedBoardBase):
    id: int
    completed_at: datetime
    class Config:
        from_attributes = True


# =========================
# GAME SESSION SCHEMAS
# =========================
class GameSessionBase(BaseModel):
    """
    Shared fields for creating and returning game sessions.
    """
    user_id: int
    board_id: int
    board_progress: str  


class GameSessionCreate(GameSessionBase):
    """
    Fields required to create a new game session.
    Non-required fields use defaults if not provided.
    """
    completion_percentage: Annotated[Optional[Decimal], Field(ge=0, le=100)] = 0.0
    current_score: Annotated[Optional[int], Field(ge=0)] = 0
    elapsed_time: Annotated[Optional[int], Field(ge=0)] = 0
    hints_used: Annotated[Optional[int], Field(ge=0)] = 0
    mistakes_made: Annotated[Optional[int], Field(ge=0)] = 0
    

class GameSessionResponse(GameSessionBase):
    """
    Returned when fetching a game session.
    Includes database-generated fields like id and timestamps.
    """
    id: int
    completion_percentage: Annotated[Decimal, Field(ge=0, le=100)]
    current_score: Annotated[int, Field(ge=0)]
    elapsed_time: Annotated[int, Field(ge=0)]
    hints_used: Annotated[int, Field(ge=0)]
    mistakes_made: Annotated[int, Field(ge=0)]
    started_at: datetime
    last_active_at: datetime
    class Config:
        from_attributes = True

class GameSessionUpdate(BaseModel):
    """
    Schema for updating fields during gameplay (e.g., score, time, board progress).
    Fields are optional since they may not all be updated in a single request.
    """
    board_progress: Optional[str]  # JSON stringified 2D list (e.g., user move updates)
    completion_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    current_score: Optional[int] = Field(None, ge=0)
    elapsed_time: Optional[int] = Field(None, ge=0)
    hints_used: Optional[int] = Field(None, ge=0)
    mistakes_made: Optional[int] = Field(None, ge=0)

    class Config:
        # Prevent serialization issues when field is None.
        # This way, None values won't be sent if not present.
        from_attributes = True

# =========================
# INCOMPLETE BOARD SCHEMAS
# =========================
class IncompleteBoardBase(BaseModel):
    user_id: int
    board_id: int
    completion_percentage: Decimal = Field(..., ge=0, le=100)
    score: int = Field(..., ge=0)

class IncompleteBoardCreate(IncompleteBoardBase):
    pass

class IncompleteBoardResponse(IncompleteBoardBase):
    id: int
    class Config:
        from_attributes = True





