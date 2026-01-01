# Sudoku Game

A full-stack Sudoku game built with React (frontend) and FastAPI (backend). This project provides a complete, playable Sudoku game with a modern UI, timer, mistake tracking, and difficulty selection.

## Project Structure

```
AI-Sudoku/
├── backend/          # FastAPI backend server
│   └── app/
│       ├── main.py              # FastAPI application entry point
│       ├── database.py          # Database connection and session management
│       ├── models/             # SQLAlchemy database models
│       ├── routers/            # API route handlers
│       ├── schemas.py          # Pydantic models for request/response validation
│       └── utils.py            # Utility functions (validation, scoring)
├── frontend/        # React frontend application
│   └── src/
│       ├── components/
│       │   └── Game.jsx        # Main Sudoku game component
│       ├── api.js              # API client functions
│       ├── App.jsx             # Main app component with routing
│       └── main.jsx            # React entry point with QueryClient setup
├── README.md        # This file
└── FUTURE_FEATURES.md  # List of potential future features
```

## Features

### Game Features
- **9x9 Sudoku Grid**: Classic Sudoku gameplay with clear visual separation of 3x3 boxes
- **Difficulty Selection**: Choose from Easy, Medium, Hard, or Random (via confirmation modal)
- **Timer**: Track your solving time with MM:SS format
- **Mistake Tracking**: Counts incorrect moves in real-time
- **Hint System**: Get up to 3 hints per game that reveal correct answers
- **Scoring System**: 
  - Base score of 10,000 points
  - +100 points for each correct answer
  - -300 points per mistake
  - -800 points per hint used
  - Time bonuses based on completion speed
  - Perfect game bonus (+2,000 points)
  - Difficulty multipliers (Easy: 1.0x, Medium: 1.5x, Hard: 2.0x)
- **Visual Feedback**: 
  - Highlights selected cell and related cells (row, column, box)
  - Different colors for pre-filled (blue) vs user-filled (green) cells
  - Error highlighting (red) for incorrect moves
  - Number highlighting - click any number to see all instances
  - Dark background highlighting for selected numbers
- **Light/Dark Mode**: Toggle between light and dark themes
- **Keyboard Support**: 
  - Number keys (1-9) to input numbers
  - Arrow keys for navigation
  - Backspace/Delete to clear cells
- **Win Detection**: Automatically detects when puzzle is complete
- **Score Modal**: Detailed breakdown of final score with all bonuses and penalties
- **Instructions Modal**: Comprehensive guide on how to play Sudoku
- **New Game Confirmation**: Prevents accidental game resets with difficulty selection

### Technical Features
- **React Query**: Efficient data fetching and caching
- **Tailwind CSS v4**: Modern, responsive styling with PostCSS
- **FastAPI Backend**: RESTful API with PostgreSQL database
- **Move Validation**: Real-time validation of Sudoku rules
- **State Management**: React hooks for efficient state handling
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Prerequisites

### Option 1: Docker (Recommended)
- **Docker** and **Docker Compose** installed
- No need to install Python, Node.js, or PostgreSQL separately

### Option 2: Manual Setup
- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **PostgreSQL** (for database)
- **npm** or **yarn** (package manager)

## Setup Instructions

### Quick Start with Docker (Recommended)

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd AI-Sudoku
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your database credentials (or use defaults for development).

3. **Start all services**:
   ```bash
   docker-compose up --build
   ```
   This will start:
   - PostgreSQL database on port 5432
   - FastAPI backend on port 8000
   - React frontend on port 5173

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Populate the database** (first time only):
   ```bash
   docker-compose exec backend python app/populate_boards.py
   ```

6. **Stop all services**:
   ```bash
   docker-compose down
   ```

**Docker Commands:**
- `docker-compose up` - Start services
- `docker-compose up -d` - Start in detached mode
- `docker-compose down` - Stop and remove containers
- `docker-compose logs -f` - View logs
- `docker-compose restart <service>` - Restart a specific service
- `docker-compose exec backend bash` - Access backend container shell
- `docker-compose exec frontend sh` - Access frontend container shell

**Production Deployment:**
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Manual Setup (Without Docker)

### 1. Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend/app
   ```

2. **Create a virtual environment (if not already created):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   Create a `.env` file in the `backend/app` directory (or use the root `.env.example`):
   ```
   DB_HOST=localhost
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=your_database_name
   ```
   Or copy the example:
   ```bash
   cp .env.example .env
   ```

6. **Create the database:**
   Make sure PostgreSQL is running and create a database:
   ```sql
   CREATE DATABASE your_database_name;
   ```

7. **Populate the database with Sudoku puzzles (optional but recommended):**
   ```bash
   python populate_boards.py
   ```
   This will fetch puzzles from an external API and store them in your database.

8. **Start the backend server:**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`

### 2. Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173` (or the port Vite assigns)

## How to Play

1. **Start the game**: The game automatically loads a puzzle when you open it
2. **Select a cell**: 
   - Click on an empty cell to select it (highlighted in blue)
   - Click on a number already on the board to highlight all instances of that number
   - Related cells (same row, column, or box) are highlighted in a lighter shade
3. **Enter a number**: 
   - Click a number button (1-9) at the bottom (after selecting a cell)
   - Or use your keyboard (1-9 keys) when a cell is selected
   - Use the backspace button (⌫) or Backspace/Delete key to clear a cell
4. **Get hints**: Click the "💡 Hint" button to reveal a random correct answer (max 3 per game)
5. **Navigate**: Use arrow keys to move between cells
6. **View instructions**: Click the 📖 button in the header for detailed game instructions
7. **Toggle theme**: Click the sun/moon icon to switch between light and dark mode
8. **Start new game**: 
   - Click "New Game" button
   - Confirm in the modal that appears
   - Select your desired difficulty (Random, Easy, Medium, Hard)
   - Click "Start New Game" to begin
9. **Win the game**: Complete the puzzle correctly to see your final score with detailed breakdown

## Code Explanation

### Backend (`backend/app/routers/game.py`)

The `/game` endpoint:
- Fetches a random Sudoku board from the database
- Parses the puzzle and solution from JSON strings
- Returns them in a format the frontend can use
- Supports difficulty filtering

**Key Concepts:**
- **FastAPI**: Modern Python web framework**
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **Dependency Injection**: `Depends(get_db)` provides database sessions

### Frontend (`frontend/src/components/Game.jsx`)

The main game component manages:
- **State Management**: Uses React hooks (`useState`, `useEffect`, `useCallback`)
- **Board State**: Tracks current puzzle state, solution, and initial puzzle
- **Game Logic**: 
  - Move validation (checks row, column, and 3x3 box)
  - Win condition detection
  - Timer management
- **User Interaction**: 
  - Cell selection
  - Number input (mouse and keyboard)
  - Visual feedback

**Key React Concepts:**
- **React Query**: Handles API calls, loading states, and caching
- **Hooks**: `useState` for state, `useEffect` for side effects, `useCallback` for memoized functions
- **Event Handling**: Click and keyboard event listeners

### API Client (`frontend/src/api.js`)

Simple Axios-based client that:
- Makes GET requests to the backend
- Supports difficulty parameter
- Returns parsed JSON data

### Styling

- **Tailwind CSS**: Utility-first CSS framework
- **Responsive Design**: Works on desktop and mobile
- **Dark Theme**: Modern dark color scheme
- **Visual Feedback**: Colors indicate cell states (selected, related, error, etc.)

## Database Schema

The `Board` model stores:
- `id`: Unique identifier
- `puzzle`: JSON string of the initial puzzle (9x9 grid with 0s for empty cells)
- `solution`: JSON string of the complete solution
- `difficulty`: Difficulty level (easy, medium, hard)
- Statistics: completion rate, times played, etc.

## API Endpoints

- `GET /game?difficulty={level}`: Get a new Sudoku puzzle
  - `difficulty` can be: "easy", "medium", "hard", or "random"
  - Returns: `{ puzzle, solution, difficulty, board_id }`

## Docker Troubleshooting

### Common Docker Issues

1. **Port already in use**:
   - Change ports in `docker-compose.yml` if 5432, 8000, or 5173 are taken
   - Or stop the service using the port

2. **Database connection errors**:
   - Ensure `.env` file exists with correct credentials
   - For Docker, `DB_HOST` should be `db` (service name), not `localhost`
   - Wait for database to be healthy before starting backend

3. **Build failures**:
   - Try `docker-compose build --no-cache` to rebuild from scratch
   - Check that `requirements.txt` exists in `backend/` directory

4. **Volume permission issues** (Linux):
   - May need to adjust file permissions
   - Try `sudo chown -R $USER:$USER .` in project directory

5. **Frontend not connecting to backend**:
   - Check that `VITE_API_URL` in `docker-compose.yml` matches backend URL
   - For production, update API URL in `frontend/src/api.js`

## Troubleshooting

### Backend Issues

1. **Database connection errors**: 
   - Check your `.env` file has correct credentials
   - Ensure PostgreSQL is running
   - Verify the database exists

2. **No boards available**:
   - Run `python populate_boards.py` to populate the database
   - This fetches puzzles from an external API

3. **Import errors**:
   - Make sure you're running from the `backend/app` directory
   - Or adjust import paths in `main.py`

### Frontend Issues

1. **Tailwind styles not working**:
   - Make sure `index.css` imports Tailwind directives
   - Check `tailwind.config.js` is in the root of `frontend/`
   - Restart the dev server

2. **API connection errors**:
   - Verify backend is running on `http://127.0.0.1:8000`
   - Check CORS settings in `backend/app/main.py`
   - Check browser console for specific error messages

3. **React Query errors**:
   - Ensure `QueryClientProvider` wraps your app in `main.jsx`
   - Check that `@tanstack/react-query` is installed

## Future Enhancements

For a comprehensive list of potential features and improvements, see [FUTURE_FEATURES.md](FUTURE_FEATURES.md).

Some high-priority features being considered:
- **Notes/Pencil Marks**: Allow placing candidate numbers in cell corners
- **Undo/Redo System**: Undo last moves with history tracking
- **Statistics Dashboard**: Track games played, best times, win rates, and streaks
- **Daily Challenge**: One puzzle per day with leaderboards
- **Save/Resume Game**: Save game state and resume later
- **Practice Mode**: No timer, unlimited hints for learning
- **Multiplayer Support**: Real-time and turn-based multiplayer modes (original goal)

See [FUTURE_FEATURES.md](FUTURE_FEATURES.md) for the complete list with detailed descriptions and priority recommendations.

## Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Relational database
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Frontend
- **React 19**: UI library
- **Vite**: Build tool and dev server
- **React Query**: Data fetching and state management
- **Axios**: HTTP client
- **Tailwind CSS**: Styling framework
- **React Router**: Routing (currently minimal usage)

## License

This project is open source and available for personal use.

