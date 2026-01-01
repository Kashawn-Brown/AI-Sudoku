import requests
import json
from time import sleep
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Board

# Simple API URL to fetch Sudoku puzzles (recommended for now)
SUDOKU_API_URL = "https://sudoku-api.vercel.app/api/dosuku"
# or: https://sudoku-api.vercel.app/api/dosuku?query={newboard(limit:1){grids{value,solution,difficulty},results,message}}

# Target number of boards per difficulty
TARGET_COUNT_PER_DIFFICULTY = {
    "easy": 50,
    "medium": 50,
    "hard": 50,
    # "expert": 50
}

# Max consecutive retries allowed when no new puzzle is found
MAX_RETRIES_WITHOUT_NEW = 100


def fetch_board():
    """Fetch a single Sudoku board from the API."""
    
    try:
        response = requests.get(SUDOKU_API_URL, timeout=10)
        response.raise_for_status()

        board_data = response.json()["newboard"]["grids"][0]
        return {
            "puzzle": json.dumps(board_data["value"]),
            "solution": json.dumps(board_data["solution"]),
            "difficulty": board_data["difficulty"].lower()
        }
    
    except (requests.RequestException, KeyError, IndexError) as e:
        print(f"❌ HTTP Error: {e} | Status Code: {response.status_code}")
    except requests.exceptions.Timeout:
        print("⏳ Request timed out. The server took too long to respond.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        
    return None


def board_exists(db: Session, puzzle: str, solution: str) -> bool:
    """Check if a board already exists in the database."""
    return db.query(Board).filter_by(puzzle=puzzle, solution=solution).first() is not None


def populate_boards():
    """Populate the database with Sudoku boards until the target is met for each difficulty."""
    
    db = SessionLocal()

    # Track how many we have added for each difficulty
    difficulty_counts = {diff: 0 for diff in TARGET_COUNT_PER_DIFFICULTY}
    retry_counter = 0

    try:
        while True:
            # Stop if all difficulties are filled
            if all(difficulty_counts[diff] >= TARGET_COUNT_PER_DIFFICULTY[diff] for diff in difficulty_counts):
                print("✅ Target board count reached for all difficulties.")
                break

            board = fetch_board()
            if not board:
                continue  # Skip this round if API failed

            difficulty = board["difficulty"]
            
            # Skip unknown difficulties
            if difficulty not in TARGET_COUNT_PER_DIFFICULTY:
                print(f"Skipping unknown difficulty: {difficulty}")
                continue

            if difficulty_counts[difficulty] >= TARGET_COUNT_PER_DIFFICULTY[difficulty]:
                continue  # Already reached goal for this difficulty

            if board_exists(db, board["puzzle"], board["solution"]):
                retry_counter += 1
                if retry_counter >= MAX_RETRIES_WITHOUT_NEW:
                    print("⚠️ Stopping: Max retries reached without finding new boards.")
                    break
                continue

            # Add new board to the database
            new_board = Board(
                puzzle=board["puzzle"],
                solution=board["solution"],
                difficulty=difficulty
            )
            db.add(new_board)
            db.commit()
            db.refresh(new_board)

            difficulty_counts[difficulty] += 1
            retry_counter = 0  # Reset on successful new board

            print(f"✅ Added {difficulty.capitalize()} board | ID: {new_board.id} | Counts: {difficulty_counts}")

            # Optional: throttle to avoid overloading API
            sleep(0.25)

    finally:
        db.close()
        print("\n🎉 Done populating boards!\n")
        print("📊 Final board counts:")
        for diff, count in difficulty_counts.items():
            print(f"  - {diff.capitalize()}: {count}")


if __name__ == "__main__":
    populate_boards()
