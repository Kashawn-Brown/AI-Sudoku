import requests
import json

# External API URL that provides Sudoku puzzles
SUDOKU_API_URL = "https://sudoku-api.vercel.app/api/dosuku"

def fetch_sudoku():
    """Fetch a Sudoku puzzle from the external API."""
    try:
        response = requests.get(SUDOKU_API_URL)  # Make the GET request
        response.raise_for_status()  # Raise an error if request fails
        data = response.json()  # Parse response as JSON
        return data
    except requests.exceptions.RequestException as e:
        print("Error fetching Sudoku puzzle:", e)
        return None


def parse_sudoku_data(data):
    """Extract relevant details from the API response."""
    if not data:
        print("No data received")
        return

    try:
        # Extract the first Sudoku puzzle from the response
        board_data = data["newboard"]["grids"][0]  

        puzzle = board_data["value"]  # Unsolved board
        solution = board_data["solution"]  # Solved board
        difficulty = board_data["difficulty"]  # Difficulty level

        # Print structured data
        print("\n--- Sudoku Puzzle ---")
        print("Difficulty:", difficulty)
        print("\nPuzzle Grid:")
        for row in puzzle:
            print(row)
        
        print("\nSolution Grid:")
        for row in solution:
            print(row)

        return {
            "puzzle": json.dumps(puzzle),  # Convert list to JSON string for storage
            "solution": json.dumps(solution),
            "difficulty": difficulty.lower()  # Convert difficulty to lowercase for consistency
        }

    except KeyError as e:
        print("Error parsing Sudoku data:", e)
        return None

if __name__ == "__main__":
    # Fetch and parse Sudoku puzzle
    sudoku_data = fetch_sudoku()
    parsed_data = parse_sudoku_data(sudoku_data)

    # Print final formatted output
    if parsed_data:
        print("\nFormatted Data for Storage:")
        print(parsed_data)
