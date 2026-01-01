"""
Models package initialization.

This file makes the models directory a Python package and exports all model classes
so they can be imported using: from models import Board, User, etc.
"""

# Import all model classes
from .Board import Board
from .User import User
from .GameSession import GameSession
from .CompletedBoard import CompletedBoard
from .IncompleteBoard import IncompleteBoard

# Export all models for easy importing
__all__ = [
    "Board",
    "User",
    "GameSession",
    "CompletedBoard",
    "IncompleteBoard",
]

