import { useState, useEffect, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchSudoku } from "../api";

/**
 * Sudoku Game Component
 * 
 * This component manages the entire Sudoku game state and UI.
 * It handles:
 * - Loading puzzles from the API
 * - Displaying the 9x9 grid
 * - Cell selection and number input
 * - Move validation
 * - Timer tracking
 * - Win condition detection
 */

const Game = () => {
  // State for the current puzzle (9x9 grid with initial values)
  const [puzzle, setPuzzle] = useState(null);
  
  // State for the solution (9x9 grid with complete solution)
  const [solution, setSolution] = useState(null);
  
  // State for the current board state (what the user sees/edits)
  // This is a 9x9 array where 0 = empty cell
  const [board, setBoard] = useState(null);
  
  // State for the initial puzzle (to distinguish pre-filled vs user-filled cells)
  const [initialBoard, setInitialBoard] = useState(null);
  
  // Currently selected cell [row, col] or null
  const [selectedCell, setSelectedCell] = useState(null);
  
  // Timer state (in seconds)
  const [timer, setTimer] = useState(0);
  
  // Whether the timer is running
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  
  // Whether the game is won
  const [isWon, setIsWon] = useState(false);
  
  // Number of mistakes made
  const [mistakes, setMistakes] = useState(0);
  
  // Number of hints used
  const [hintsUsed, setHintsUsed] = useState(0);
  
  // Number of correct answers placed
  const [correctAnswers, setCorrectAnswers] = useState(0);
  
  // Show instructions modal
  const [showInstructions, setShowInstructions] = useState(false);
  
  // Score for completed game
  const [finalScore, setFinalScore] = useState(null);
  
  // Show score modal
  const [showScoreModal, setShowScoreModal] = useState(false);
  
  // Show new game confirmation modal
  const [showNewGameModal, setShowNewGameModal] = useState(false);
  
  // Selected difficulty for new game (in modal)
  const [selectedDifficulty, setSelectedDifficulty] = useState("random");
  
  // Difficulty of current puzzle
  const [difficulty, setDifficulty] = useState("random");
  
  // Theme state (light or dark mode) - default to light mode
  const [isLightMode, setIsLightMode] = useState(true);
  
  // Currently highlighted number (for highlighting all instances on the board)
  const [highlightedNumber, setHighlightedNumber] = useState(null);

  // Fetch a new Sudoku puzzle from the API
  // useQuery automatically handles loading states and caching
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["sudoku", difficulty],
    queryFn: () => fetchSudoku(difficulty),
    // Don't automatically refetch - we'll manually trigger with refetch()
    enabled: false, // Start disabled, we'll fetch on mount or when difficulty changes
  });

  // Initialize game when data is fetched
  useEffect(() => {
    if (data) {
      // Parse the puzzle and solution from the API response
      const puzzleData = data.puzzle;
      const solutionData = data.solution;
      
      // Create a deep copy of the puzzle for the initial board state
      // This helps us identify which cells were pre-filled (can't be edited)
      const initial = puzzleData.map(row => [...row]);
      
      // Set all the state
      setPuzzle(puzzleData);
      setSolution(solutionData);
      setBoard(puzzleData.map(row => [...row])); // Deep copy for editing
      setInitialBoard(initial);
      
      // Reset game state
      setSelectedCell(null);
      setTimer(0);
      setIsTimerRunning(true);
      setIsWon(false);
      setMistakes(0);
      setHintsUsed(0);
      setCorrectAnswers(0);
      setFinalScore(null);
      setShowScoreModal(false);
    }
  }, [data]);

  // Fetch a new game when component mounts
  useEffect(() => {
    refetch();
  }, [difficulty, refetch]);

  // Timer effect - increments every second when running
  useEffect(() => {
    let interval = null;
    if (isTimerRunning && !isWon) {
      interval = setInterval(() => {
        setTimer((prevTimer) => prevTimer + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    // Cleanup interval on unmount or when dependencies change
    return () => clearInterval(interval);
  }, [isTimerRunning, isWon]);

  /**
   * Validates if a number can be placed in a cell according to Sudoku rules
   * 
   * Rules:
   * 1. No duplicate in the same row
   * 2. No duplicate in the same column
   * 3. No duplicate in the same 3x3 box
   * 
   * @param {number} row - Row index (0-8)
   * @param {number} col - Column index (0-8)
   * @param {number} value - The number to check (1-9)
   * @returns {boolean} True if the move is valid
   */
  const isValidMove = useCallback((row, col, value) => {
    if (!board || value === 0) return true; // Empty cells are always "valid"
    
    // Check row for duplicates
    for (let j = 0; j < 9; j++) {
      if (j !== col && board[row][j] === value) {
        return false;
      }
    }
    
    // Check column for duplicates
    for (let i = 0; i < 9; i++) {
      if (i !== row && board[i][col] === value) {
        return false;
      }
    }
    
    // Check 3x3 box for duplicates
    // Calculate which box the cell is in
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;
    
    for (let i = boxRow; i < boxRow + 3; i++) {
      for (let j = boxCol; j < boxCol + 3; j++) {
        if (i !== row && j !== col && board[i][j] === value) {
          return false;
        }
      }
    }
    
    return true;
  }, [board]);

  /**
   * Checks if the current board matches the solution (win condition)
   */
  const checkWin = useCallback(() => {
    if (!board || !solution) return false;
    
    // Compare every cell
    for (let i = 0; i < 9; i++) {
      for (let j = 0; j < 9; j++) {
        if (board[i][j] !== solution[i][j]) {
          return false;
        }
      }
    }
    
    return true;
  }, [board, solution]);

  /**
   * Handles placing a number in a cell
   * 
   * @param {number} value - The number to place (1-9, or 0 to clear)
   */
  const handleNumberInput = useCallback((value) => {
    if (!board || !selectedCell || isWon) return;
    
    const [row, col] = selectedCell;
    
    // Don't allow editing pre-filled cells
    if (initialBoard[row][col] !== 0) {
      return;
    }
    
    // Create a new board state
    const newBoard = board.map(r => [...r]);
    
    // Track if we're clearing a correct answer (to remove points)
    const wasCorrect = board[row][col] !== 0 && solution && solution[row][col] === board[row][col];
    
    // If placing the same number, clear it instead (toggle behavior)
    if (newBoard[row][col] === value) {
      newBoard[row][col] = 0;
      // If clearing a correct answer, remove the point
      if (wasCorrect && initialBoard[row][col] === 0) {
        setCorrectAnswers((prev) => Math.max(0, prev - 1));
      }
    } else {
      newBoard[row][col] = value;
      
      // Check if this move is correct according to the solution
      if (value !== 0 && solution) {
        if (solution[row][col] === value) {
          // This is a correct answer - only count if cell was previously empty or wrong
          const wasEmpty = board[row][col] === 0;
          const wasWrong = board[row][col] !== 0 && board[row][col] !== solution[row][col];
          if (wasEmpty || wasWrong) {
            setCorrectAnswers((prev) => prev + 1);
          }
        } else {
          // This is a mistake
          setMistakes((prev) => prev + 1);
        }
      }
    }
    
    setBoard(newBoard);
    
    // If a number was placed (not cleared), highlight all instances of that number
    if (value !== 0) {
      setHighlightedNumber(value);
    } else {
      // If clearing, also clear highlighting
      setHighlightedNumber(null);
    }
    
    // Check for win condition after a short delay (to allow state to update)
    setTimeout(() => {
      const newBoardForCheck = newBoard.map(r => [...r]);
      let isComplete = true;
      for (let i = 0; i < 9; i++) {
        for (let j = 0; j < 9; j++) {
          if (newBoardForCheck[i][j] !== solution[i][j]) {
            isComplete = false;
            break;
          }
        }
        if (!isComplete) break;
      }
      
      if (isComplete) {
        setIsWon(true);
        setIsTimerRunning(false);
      }
    }, 100);
  }, [board, selectedCell, initialBoard, solution, isWon]);

  /**
   * Handles keyboard input for number entry
   */
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (!selectedCell || isWon) return;
      
      // Handle number keys 1-9
      if (e.key >= "1" && e.key <= "9") {
        handleNumberInput(parseInt(e.key));
      }
      // Handle backspace/delete to clear
      else if (e.key === "Backspace" || e.key === "Delete") {
        handleNumberInput(0);
      }
      // Handle arrow keys for navigation
      else if (e.key === "ArrowUp" && selectedCell[0] > 0) {
        setSelectedCell([selectedCell[0] - 1, selectedCell[1]]);
      } else if (e.key === "ArrowDown" && selectedCell[0] < 8) {
        setSelectedCell([selectedCell[0] + 1, selectedCell[1]]);
      } else if (e.key === "ArrowLeft" && selectedCell[1] > 0) {
        setSelectedCell([selectedCell[0], selectedCell[1] - 1]);
      } else if (e.key === "ArrowRight" && selectedCell[1] < 8) {
        setSelectedCell([selectedCell[0], selectedCell[1] + 1]);
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [selectedCell, handleNumberInput, isWon]);

  /**
   * Handles clicking outside the sudoku grid to reset selection
   * But allows clicks on number buttons and other game controls
   */
  useEffect(() => {
    const handleClickOutside = (e) => {
      // Check if click is on any interactive game element - don't reset
      const isGameControl = e.target.closest('[data-game-control]');
      const isNumberButton = e.target.closest('[data-number-button]');
      const isGrid = e.target.closest('[data-sudoku-grid]');
      const isButton = e.target.tagName === 'BUTTON';
      const isSelect = e.target.tagName === 'SELECT';
      
      // Only reset if clicking on the page background (not on any interactive element)
      // This allows clicking buttons/selects without clearing selection
      if (!isGrid && !isGameControl && !isNumberButton && !isButton && !isSelect) {
        setSelectedCell(null);
        setHighlightedNumber(null);
      }
    };

    // Use click event (not mousedown) so button clicks process first
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  /**
   * Formats the timer as MM:SS
   */
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  /**
   * Handles clicking the new game button - shows confirmation modal
   */
  const handleNewGameClick = () => {
    setShowNewGameModal(true);
    setSelectedDifficulty(difficulty); // Pre-select current difficulty
  };

  /**
   * Actually starts a new game after user confirms and selects difficulty
   */
  const handleNewGameConfirm = () => {
    setDifficulty(selectedDifficulty); // Update difficulty
    setHighlightedNumber(null); // Reset highlighted number
    setShowScoreModal(false); // Close score modal if open
    setShowNewGameModal(false); // Close confirmation modal
    refetch(); // Start new game
  };


  /**
   * Calculates the current score during gameplay (without time bonus)
   * This is shown in real-time and doesn't change every second
   * Formula:
   * Base Score = 10,000
   * + Correct Answer Bonus: (correct answers × 100)
   * - Mistake Penalty: (mistakes × 300)
   * - Hint Penalty: (hints × 800)
   * × Difficulty Multiplier: Easy (1.0), Medium (1.5), Hard (2.0)
   */
  const calculateLiveScore = useCallback(() => {
    const BASE_SCORE = 10000;
    const CORRECT_ANSWER_BONUS = 100; // Points gained per correct answer
    const MISTAKE_PENALTY = 300; // Points lost per mistake
    const HINT_PENALTY = 800; // Points lost per hint
    
    // Difficulty multipliers
    const difficultyMultipliers = {
      easy: 1.0,
      medium: 1.5,
      hard: 2.0,
      random: 1.25, // Average of easy and medium
    };
    
    // Calculate base score with bonuses and penalties (no time component)
    let score = BASE_SCORE;
    score += correctAnswers * CORRECT_ANSWER_BONUS;
    score -= mistakes * MISTAKE_PENALTY;
    score -= hintsUsed * HINT_PENALTY;
    
    // Apply difficulty multiplier
    const multiplier = difficultyMultipliers[difficulty.toLowerCase()] || 1.0;
    score = Math.round(score * multiplier);
    
    // Ensure score doesn't go below 0
    score = Math.max(0, score);
    
    return score;
  }, [correctAnswers, mistakes, hintsUsed, difficulty]);

  /**
   * Calculates the final score based on time, mistakes, hints, and difficulty
   * Formula:
   * Base Score = 10,000
   * + Correct Answer Bonus: (correct answers × 100)
   * - Mistake Penalty: (mistakes × 300)
   * - Hint Penalty: (hints × 800)
   * × Difficulty Multiplier: Easy (1.0), Medium (1.5), Hard (2.0)
   * + Time Bonus: Based on completion time (faster = bigger bonus)
   *   - Under 3 minutes: +3,000
   *   - Under 5 minutes: +2,000
   *   - Under 10 minutes: +1,000
   *   - Under 15 minutes: +500
   * + Perfect Game Bonus: +2,000 (if mistakes = 0 AND hints = 0)
   */
  const calculateScore = useCallback(() => {
    const BASE_SCORE = 10000;
    const CORRECT_ANSWER_BONUS = 100; // Points gained per correct answer
    const MISTAKE_PENALTY = 300; // Points lost per mistake
    const HINT_PENALTY = 800; // Points lost per hint
    const PERFECT_BONUS = 2000; // Bonus for no mistakes and no hints
    
    // Time bonus thresholds (in seconds)
    const TIME_BONUS_3MIN = 3000; // 3 minutes = 180 seconds
    const TIME_BONUS_5MIN = 2000; // 5 minutes = 300 seconds
    const TIME_BONUS_10MIN = 1000; // 10 minutes = 600 seconds
    const TIME_BONUS_15MIN = 500; // 15 minutes = 900 seconds
    
    // Difficulty multipliers
    const difficultyMultipliers = {
      easy: 1.0,
      medium: 1.5,
      hard: 2.0,
      random: 1.25, // Average of easy and medium
    };
    
    // Calculate base score with bonuses and penalties
    let score = BASE_SCORE;
    score += correctAnswers * CORRECT_ANSWER_BONUS;
    score -= mistakes * MISTAKE_PENALTY;
    score -= hintsUsed * HINT_PENALTY;
    
    // Calculate time bonus based on completion time
    let timeBonus = 0;
    if (timer < 180) { // Under 3 minutes
      timeBonus = TIME_BONUS_3MIN;
    } else if (timer < 300) { // Under 5 minutes
      timeBonus = TIME_BONUS_5MIN;
    } else if (timer < 600) { // Under 10 minutes
      timeBonus = TIME_BONUS_10MIN;
    } else if (timer < 900) { // Under 15 minutes
      timeBonus = TIME_BONUS_15MIN;
    }
    
    // Add time bonus
    score += timeBonus;
    
    // Apply difficulty multiplier
    const multiplier = difficultyMultipliers[difficulty.toLowerCase()] || 1.0;
    score = Math.round(score * multiplier);
    
    // Add perfect game bonus
    const isPerfect = mistakes === 0 && hintsUsed === 0;
    if (isPerfect) {
      score += PERFECT_BONUS;
    }
    
    // Ensure score doesn't go below 0
    score = Math.max(0, score);
    
    setFinalScore({
      total: score,
      base: BASE_SCORE,
      mistakePenalty: mistakes * MISTAKE_PENALTY,
      hintPenalty: hintsUsed * HINT_PENALTY,
      correctAnswers: correctAnswers,
      correctAnswerBonus: correctAnswers * CORRECT_ANSWER_BONUS,
      timeBonus: timeBonus,
      multiplier: multiplier,
      perfectBonus: isPerfect ? PERFECT_BONUS : 0,
      difficulty: difficulty,
      time: timer,
      mistakes: mistakes,
      hints: hintsUsed,
    });
    
    // Show score modal
    setShowScoreModal(true);
  }, [timer, mistakes, hintsUsed, difficulty]);
  
  // Calculate score when game is won
  useEffect(() => {
    if (isWon && !finalScore) {
      calculateScore();
    }
  }, [isWon, finalScore, calculateScore]);

  /**
   * Handles using a hint - reveals a random empty cell with the correct solution
   * Limited to 3 hints per game
   */
  const handleHint = useCallback(() => {
    if (!board || !solution || !initialBoard || isWon) return;
    
    // Limit hints to 3 per game
    if (hintsUsed >= 3) return;
    
    // Find all empty cells (cells that are 0 and were not pre-filled)
    const emptyCells = [];
    for (let i = 0; i < 9; i++) {
      for (let j = 0; j < 9; j++) {
        // Only consider cells that are empty and were not in the initial puzzle
        if (board[i][j] === 0 && initialBoard[i][j] === 0) {
          emptyCells.push([i, j]);
        }
      }
    }
    
    // If there are no empty cells, can't give a hint
    if (emptyCells.length === 0) return;
    
    // Pick a random empty cell
    const randomCell = emptyCells[Math.floor(Math.random() * emptyCells.length)];
    const [row, col] = randomCell;
    
    // Get the correct solution value for this cell
    const correctValue = solution[row][col];
    
    // Update the board with the correct value
    const newBoard = board.map(r => [...r]);
    newBoard[row][col] = correctValue;
    setBoard(newBoard);
    
    // Increment hints used
    setHintsUsed((prev) => prev + 1);
    
    // Select the cell that was revealed
    setSelectedCell([row, col]);
    
    // Highlight all instances of the revealed number
    setHighlightedNumber(correctValue);
  }, [board, solution, initialBoard, isWon, hintsUsed]);

  /**
   * Checks if a number is complete (all 9 instances are correctly placed)
   * A number is complete when there are exactly 9 cells with that number value
   * and all of them match the solution
   * 
   * @param {number} num - The number to check (1-9)
   * @returns {boolean} True if the number is complete
   */
  const isNumberComplete = useCallback((num) => {
    if (!board || !solution) return false;
    
    let count = 0;
    // Count how many cells have this number and check if they're all correct
    for (let i = 0; i < 9; i++) {
      for (let j = 0; j < 9; j++) {
        if (board[i][j] === num) {
          // If the number doesn't match the solution, it's not complete
          if (solution[i][j] !== num) {
            return false;
          }
          count++;
        }
      }
    }
    
    // Number is complete if we found exactly 9 instances, all correct
    return count === 9;
  }, [board, solution]);

  // Theme classes - reusable styling based on light/dark mode
  const bgMain = isLightMode ? "bg-gray-50" : "bg-gray-900";
  const textMain = isLightMode ? "text-gray-900" : "text-white";
  const bgCard = isLightMode ? "bg-white" : "bg-gray-800";
  const borderColor = isLightMode ? "border-gray-300" : "border-gray-700";
  const bgInput = isLightMode ? "bg-gray-100" : "bg-gray-700";
  const bgInputHover = isLightMode ? "hover:bg-gray-200" : "hover:bg-gray-600";
  const textMuted = isLightMode ? "text-gray-600" : "text-gray-400";
  const bgSelected = isLightMode ? "bg-blue-400 ring-blue-300" : "bg-blue-600 ring-blue-400";
  const bgRelated = isLightMode ? "bg-blue-50" : "bg-gray-700";
  const textInitial = isLightMode ? "text-blue-700" : "text-blue-300";
  const textUser = isLightMode ? "text-green-700" : "text-green-300";
  const bgError = isLightMode ? "bg-red-100 text-red-800" : "bg-red-900 text-red-200";

  // Loading state
  if (isLoading) {
    return (
      <div className={`flex items-center justify-center min-h-screen ${bgMain} ${textMain}`}>
        <div className="text-center">
          <div className="text-2xl mb-4">Loading Sudoku...</div>
          <div className={`animate-spin rounded-full h-12 w-12 border-b-2 ${isLightMode ? "border-gray-900" : "border-white"} mx-auto`}></div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`flex items-center justify-center min-h-screen ${bgMain} ${textMain}`}>
        <div className="text-center">
          <div className={`text-2xl mb-4 ${isLightMode ? "text-red-600" : "text-red-400"}`}>Error loading puzzle</div>
          <div className={`${textMuted} mb-4`}>{error.message}</div>
          <button
            onClick={handleNewGameClick}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // No board loaded yet
  if (!board || !solution) {
    return (
      <div className={`flex items-center justify-center min-h-screen ${bgMain} ${textMain}`}>
        <div className="text-center">
          <div className="text-2xl mb-4">No puzzle loaded</div>
          <button
            onClick={handleNewGameClick}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            Load Puzzle
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${bgMain} ${textMain} p-4`}>
      <div className="max-w-4xl mx-auto">
        {/* Header with game info and controls */}
        <div className="mb-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <h1 className="text-3xl font-bold">Sudoku Game</h1>
          
          <div className="flex items-center gap-4">
            {/* Instructions button */}
            <button
              onClick={() => setShowInstructions(true)}
              className={`px-4 py-2 rounded-lg font-semibold transition ${isLightMode ? "bg-green-500 hover:bg-green-600" : "bg-green-600 hover:bg-green-700"} text-white`}
              title="How to play Sudoku"
            >
              📖
            </button>
            
            {/* Theme toggle button */}
            <button
              onClick={() => setIsLightMode(!isLightMode)}
              className={`px-3 py-2 rounded-lg transition ${isLightMode ? "bg-yellow-500 hover:bg-yellow-600" : "bg-gray-700 hover:bg-gray-600"} text-white`}
              title={isLightMode ? "Switch to dark mode" : "Switch to light mode"}
            >
              {isLightMode ? "🌙" : "☀️"}
            </button>
            
            {/* New game button */}
            <button
              onClick={handleNewGameClick}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
            >
              New Game
            </button>
          </div>
        </div>

        {/* Game stats */}
        <div className="mb-4 flex flex-wrap justify-center gap-6 text-lg">
          <div className={`${bgCard} px-4 py-2 rounded-lg shadow ${isLightMode ? "shadow-gray-200" : "shadow-gray-900"}`}>
            <span className={textMuted}>Time: </span>
            <span className="font-mono font-bold">{formatTime(timer)}</span>
          </div>
          <div className={`${bgCard} px-4 py-2 rounded-lg shadow ${isLightMode ? "shadow-gray-200" : "shadow-gray-900"}`}>
            <span className={textMuted}>Mistakes: </span>
            <span className={`font-bold ${isLightMode ? "text-red-600" : "text-red-400"}`}>{mistakes}</span>
          </div>
          <div className={`${bgCard} px-4 py-2 rounded-lg shadow ${isLightMode ? "shadow-gray-200" : "shadow-gray-900"}`}>
            <span className={textMuted}>Hints: </span>
            <span className={`font-bold ${isLightMode ? "text-yellow-600" : "text-yellow-400"}`}>{hintsUsed}</span>
          </div>
          <div className={`${bgCard} px-4 py-2 rounded-lg shadow ${isLightMode ? "shadow-gray-200" : "shadow-gray-900"}`}>
            <span className={textMuted}>Difficulty: </span>
            <span className="font-bold capitalize">{data?.difficulty || "unknown"}</span>
          </div>
        </div>

        {/* Score display - bigger and above the table */}
        <div className="mb-6 flex justify-center">
          <div className={`${bgCard} px-8 py-4 rounded-lg shadow-lg ${isLightMode ? "shadow-gray-200" : "shadow-gray-900"}`}>
            <div className="text-center">
              {/* <div className={`text-sm ${textMuted} mb-1`}>Score</div> */}
              <div className={`text-3xl font-bold ${isLightMode ? "text-blue-600" : "text-blue-400"}`}>
                {finalScore ? finalScore.total.toLocaleString() : calculateLiveScore().toLocaleString()}
              </div>
            </div>
          </div>
        </div>

        {/* Win message overlay */}
        {isWon && (
          <div className={`mb-6 ${isLightMode ? "bg-green-500" : "bg-green-600"} text-white p-4 rounded-lg text-center shadow-lg`}>
            <div className="text-2xl font-bold mb-2">🎉 Congratulations! You Won! 🎉</div>
            <div className="text-lg">
              Completed in {formatTime(timer)} with {mistakes} mistake{mistakes !== 1 ? "s" : ""}
            </div>
          </div>
        )}

        {/* Sudoku grid container */}
        <div className="flex flex-col items-center gap-6">
          {/* The 9x9 Sudoku grid */}
          <div className={`${bgCard} p-4 rounded-lg shadow-lg ${isLightMode ? "shadow-gray-300" : "shadow-gray-900"}`} data-sudoku-grid>
            <div className={`grid grid-cols-9 gap-0 border-2 ${isLightMode ? "border-gray-600" : "border-gray-500"}`}>
              {board.map((row, rowIndex) =>
                row.map((cell, colIndex) => {
                  // Determine if this cell was pre-filled (initial puzzle)
                  const isInitial = initialBoard[rowIndex][colIndex] !== 0;
                  
                  // Determine if this cell is selected
                  const isSelected =
                    selectedCell &&
                    selectedCell[0] === rowIndex &&
                    selectedCell[1] === colIndex;
                  
                  // Determine if this cell has an error (doesn't match solution)
                  const hasError =
                    cell !== 0 &&
                    solution[rowIndex][colIndex] !== cell;
                  
                  // Determine if this cell is in the same row/col/box as selected
                  const isRelated =
                    selectedCell &&
                    (selectedCell[0] === rowIndex ||
                      selectedCell[1] === colIndex ||
                      (Math.floor(selectedCell[0] / 3) === Math.floor(rowIndex / 3) &&
                        Math.floor(selectedCell[1] / 3) === Math.floor(colIndex / 3)));
                  
                  // Determine if this cell contains the highlighted number
                  const isHighlighted = highlightedNumber !== null && cell === highlightedNumber;
                  
                  // Calculate box borders for visual separation (3x3 boxes)
                  const isBoxTop = rowIndex % 3 === 0;
                  const isBoxLeft = colIndex % 3 === 0;
                  const isBoxRight = (colIndex + 1) % 3 === 0;
                  const isBoxBottom = (rowIndex + 1) % 3 === 0;

                  return (
                    <div
                      key={`${rowIndex}-${colIndex}`}
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent event from bubbling to document
                        
                        // If clicking on a cell with a number, highlight all instances of that number
                        // Don't select the cell, just highlight
                        if (cell !== 0) {
                          // Toggle highlighting: if same number clicked, deselect it
                          if (highlightedNumber === cell) {
                            setHighlightedNumber(null);
                            setSelectedCell(null); // Clear cell selection when deselecting number
                          } else {
                            setHighlightedNumber(cell);
                            setSelectedCell(null); // Clear cell selection when highlighting number
                          }
                        } else {
                          // If clicking on an empty cell, select it and show related cells
                          // Clear number highlighting when selecting a cell
                          setHighlightedNumber(null);
                          // Only allow selecting empty cells or user-filled cells (not pre-filled)
                          if (!isInitial || cell === 0) {
                            setSelectedCell([rowIndex, colIndex]);
                          }
                        }
                      }}
                      className={`
                        w-12 h-12 md:w-14 md:h-14
                        flex items-center justify-center
                        border ${isLightMode ? "border-gray-300" : "border-gray-600"}
                        cursor-pointer
                        transition-all
                        ${isBoxTop ? `border-t-2 ${isLightMode ? "border-t-gray-500" : "border-t-gray-500"}` : ""}
                        ${isBoxLeft ? `border-l-2 ${isLightMode ? "border-l-gray-500" : "border-l-gray-500"}` : ""}
                        ${isBoxRight ? `border-r-2 ${isLightMode ? "border-r-gray-500" : "border-r-gray-500"}` : ""}
                        ${isBoxBottom ? `border-b-2 ${isLightMode ? "border-b-gray-500" : "border-b-gray-500"}` : ""}
                        ${isSelected ? `${bgSelected} ring-2` : ""}
                        ${!isSelected && isRelated && selectedCell ? bgRelated : ""}
                        ${isHighlighted && cell !== 0 ? (isLightMode ? "bg-gray-800 text-white font-bold" : "bg-gray-950 text-white font-bold") : ""}
                        ${isInitial ? `font-bold ${textInitial}` : textMain}
                        ${hasError ? bgError : ""}
                        ${!isInitial && cell !== 0 && !hasError ? textUser : ""}
                        ${!isSelected && !isRelated && !isHighlighted && !hasError ? (isLightMode ? "hover:bg-gray-100" : "hover:bg-gray-700") : ""}
                        ${isLightMode && !isSelected && !isRelated && !isHighlighted && !hasError ? "bg-white" : ""}
                        ${!isLightMode && !isSelected && !isRelated && !isHighlighted && !hasError ? "bg-gray-800" : ""}
                      `}
                    >
                      {cell !== 0 ? cell : ""}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Number input pad */}
          <div className={`${bgCard} p-4 rounded-lg shadow-lg ${isLightMode ? "shadow-gray-300" : "shadow-gray-900"}`} data-game-control>
            <div className={`text-center mb-2 ${textMuted} text-sm`}>
              Click an empty cell to select it, or click a number on the board to highlight all instances. Click outside to reset.
            </div>
            <div className="grid grid-cols-9 gap-2">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => {
                const isComplete = isNumberComplete(num);
                
                return (
                  <button
                    key={num}
                    data-number-button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      // Don't do anything if game is won or number is complete
                      if (isWon || isComplete) return;
                      // Only input the number if a cell is selected
                      if (selectedCell) {
                        handleNumberInput(num);
                      }
                    }}
                    className={`
                      w-12 h-12 md:w-14 md:h-14
                      rounded-lg
                      font-bold text-xl
                      transition
                      ${isComplete 
                        ? `${isLightMode ? "bg-gray-300 text-gray-500" : "bg-gray-700 text-gray-500"} cursor-not-allowed opacity-60` 
                        : `${bgInput} ${bgInputHover} ${textMain} ${selectedCell ? "hover:scale-105 cursor-pointer" : "opacity-50 cursor-pointer"}`
                      }
                    `}
                    title={isComplete ? `All ${num}'s are correctly placed` : selectedCell ? `Place ${num} in selected cell` : "Select a cell first"}
                  >
                    {num}
                  </button>
                );
              })}
            </div>
            <div className="flex gap-2 mt-2">
              <button
                onClick={handleHint}
                disabled={isWon || hintsUsed >= 3}
                className={`flex-1 py-2 ${isLightMode ? "bg-purple-500 hover:bg-purple-600" : "bg-purple-600 hover:bg-purple-700"} text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed font-semibold`}
                title={hintsUsed >= 3 ? "Maximum 3 hints per game" : `Reveal a random empty cell (${3 - hintsUsed} remaining)`}
              >
                💡 Hint {hintsUsed > 0 && `(${3 - hintsUsed})`}
              </button>
              <button
                onClick={() => {
                  if (selectedCell) {
                    handleNumberInput(0);
                  }
                }}
                disabled={!selectedCell || isWon}
                className={`flex-1 py-2 ${isLightMode ? "bg-gray-500 hover:bg-gray-600" : "bg-gray-600 hover:bg-gray-700"} text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed font-semibold`}
                title="Backspace - Clear selected cell"
              >
                ⌫
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Instructions Modal */}
      {showInstructions && (
        <div 
          className={`fixed inset-0 ${isLightMode ? "bg-gray-900/40" : "bg-gray-950/60"} backdrop-blur-sm flex items-center justify-center z-50 p-4`}
          onClick={() => setShowInstructions(false)}
        >
          <div 
            className={`${bgCard} rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 ${textMain}`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">How to Play Sudoku</h2>
              <button
                onClick={() => setShowInstructions(false)}
                className={`text-2xl ${textMuted} hover:${textMain} transition`}
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <section>
                <h3 className="text-xl font-semibold mb-2">Objective</h3>
                <p className={textMuted}>
                  Fill the 9×9 grid so that every row, every column, and every 3×3 box contains the digits 1 through 9 exactly once.
                </p>
              </section>

              <section>
                <h3 className="text-xl font-semibold mb-2">Basic Rules</h3>
                <ul className={`list-disc list-inside space-y-1 ${textMuted}`}>
                  <li>Each row must contain all digits 1-9 without repetition</li>
                  <li>Each column must contain all digits 1-9 without repetition</li>
                  <li>Each 3×3 box (outlined with thicker borders) must contain all digits 1-9 without repetition</li>
                  <li>Some numbers are pre-filled (shown in blue) - these cannot be changed</li>
                </ul>
              </section>

              <section>
                <h3 className="text-xl font-semibold mb-2">How to Play</h3>
                <ol className={`list-decimal list-inside space-y-2 ${textMuted}`}>
                  <li>
                    <strong className={textMain}>Select a cell:</strong> Click on any empty cell (white/gray) to select it. 
                    The selected cell will be highlighted in blue, and related cells (same row, column, or box) will be highlighted in a lighter shade.
                  </li>
                  <li>
                    <strong className={textMain}>Place a number:</strong> Once a cell is selected, click one of the number buttons (1-9) 
                    at the bottom to place that number in the selected cell.
                  </li>
                  <li>
                    <strong className={textMain}>Highlight numbers:</strong> Click on any number already on the board to highlight 
                    all other instances of that same number. This helps you see where numbers are placed.
                  </li>
                  <li>
                    <strong className={textMain}>Clear a cell:</strong> Select a cell you've filled, then click the "Clear" button 
                    or the backspace (⌫) button to remove the number.
                  </li>
                  <li>
                    <strong className={textMain}>Get a hint:</strong> Click the "💡 Hint" button to reveal a random empty cell with 
                    the correct number. You can use up to 3 hints per game.
                  </li>
                </ol>
              </section>

              <section>
                <h3 className="text-xl font-semibold mb-2">Visual Indicators</h3>
                <ul className={`space-y-2 ${textMuted}`}>
                  <li>
                    <span className={`font-bold ${textInitial}`}>Blue numbers</span> - Pre-filled numbers that cannot be changed
                  </li>
                  <li>
                    <span className={`font-bold ${textUser}`}>Green numbers</span> - Numbers you've placed
                  </li>
                  <li>
                    <span className={`font-bold ${isLightMode ? "text-red-600" : "text-red-400"}`}>Red background</span> - Incorrect number placement
                  </li>
                  <li>
                    <span className={`font-bold ${isLightMode ? "text-gray-800" : "text-gray-950"}`}>Dark background</span> - Highlighted number instances
                  </li>
                  <li>
                    <span className={`font-bold ${isLightMode ? "text-blue-600" : "text-blue-400"}`}>Blue highlight</span> - Selected cell
                  </li>
                  <li>
                    <span className={`font-bold ${isLightMode ? "text-gray-500" : "text-gray-400"}`}>Grayed out buttons</span> - Numbers that are completely and correctly placed (all 9 instances)
                  </li>
                </ul>
              </section>

              <section>
                <h3 className="text-xl font-semibold mb-2">Tips</h3>
                <ul className={`list-disc list-inside space-y-1 ${textMuted}`}>
                  <li>Start by looking for cells that can only have one possible number</li>
                  <li>Use the number highlighting feature to see where numbers are already placed</li>
                  <li>Pay attention to the 3×3 boxes - they're just as important as rows and columns</li>
                  <li>If you make a mistake, the cell will turn red. Fix it to continue</li>
                  <li>Use hints sparingly - you only get 3 per game!</li>
                </ul>
              </section>

              <section>
                <h3 className="text-xl font-semibold mb-2">Game Features</h3>
                <ul className={`list-disc list-inside space-y-1 ${textMuted}`}>
                  <li><strong>Timer:</strong> Tracks how long you've been playing</li>
                  <li><strong>Mistakes:</strong> Counts incorrect placements (shown in red)</li>
                  <li><strong>Hints:</strong> Shows how many hints you've used (max 3)</li>
                  <li><strong>Difficulty:</strong> Choose Easy, Medium, Hard, or Random</li>
                  <li><strong>Theme:</strong> Toggle between light and dark mode</li>
                </ul>
              </section>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowInstructions(false)}
                className={`px-6 py-2 rounded-lg font-semibold transition ${isLightMode ? "bg-blue-500 hover:bg-blue-600" : "bg-blue-600 hover:bg-blue-700"} text-white`}
              >
                Got it!
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Score Modal - Shows when game is won */}
      {showScoreModal && finalScore && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowScoreModal(false)}
        >
          <div 
            className={`${bgCard} rounded-lg shadow-xl max-w-md w-full p-6 ${textMain}`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">🎉 Congratulations!</h2>
              <button
                onClick={() => setShowScoreModal(false)}
                className={`text-2xl ${textMuted} hover:${textMain} transition`}
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              {/* Final Score */}
              <div className={`text-center py-4 rounded-lg ${isLightMode ? "bg-blue-50" : "bg-blue-900"}`}>
                <div className={`text-sm ${textMuted} mb-1`}>Final Score</div>
                <div className="text-4xl font-bold text-blue-600">{finalScore.total.toLocaleString()}</div>
              </div>

              {/* Score Breakdown */}
              <div className="space-y-2">
                <h3 className="font-semibold text-lg">Score Breakdown</h3>
                
                <div className="flex justify-between">
                  <span className={textMuted}>Base Score:</span>
                  <span className="font-semibold">+{finalScore.base.toLocaleString()}</span>
                </div>
                
                {finalScore.correctAnswerBonus > 0 && (
                  <div className="flex justify-between">
                    <span className={textMuted}>Correct Answers ({finalScore.correctAnswers}):</span>
                    <span className={`font-semibold ${isLightMode ? "text-green-600" : "text-green-400"}`}>
                      +{finalScore.correctAnswerBonus.toLocaleString()}
                    </span>
                  </div>
                )}
                
                {finalScore.timeBonus > 0 && (
                  <div className="flex justify-between">
                    <span className={textMuted}>Time Bonus ({formatTime(finalScore.time)}):</span>
                    <span className={`font-semibold ${isLightMode ? "text-green-600" : "text-green-400"}`}>
                      +{finalScore.timeBonus.toLocaleString()}
                    </span>
                  </div>
                )}
                
                <div className="flex justify-between">
                  <span className={textMuted}>Mistakes ({finalScore.mistakes}):</span>
                  <span className={`font-semibold ${isLightMode ? "text-red-600" : "text-red-400"}`}>
                    -{finalScore.mistakePenalty.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className={textMuted}>Hints ({finalScore.hints}):</span>
                  <span className={`font-semibold ${isLightMode ? "text-red-600" : "text-red-400"}`}>
                    -{finalScore.hintPenalty.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className={textMuted}>Difficulty ({finalScore.difficulty}):</span>
                  <span className="font-semibold">×{finalScore.multiplier}</span>
                </div>
                
                {finalScore.perfectBonus > 0 && (
                  <div className="flex justify-between">
                    <span className={textMuted}>Perfect Game Bonus:</span>
                    <span className={`font-semibold ${isLightMode ? "text-green-600" : "text-green-400"}`}>
                      +{finalScore.perfectBonus.toLocaleString()}
                    </span>
                  </div>
                )}
                
                
                <div className={`border-t ${borderColor} pt-2 mt-2`}>
                  <div className="flex justify-between text-lg font-bold">
                    <span>Total Score:</span>
                    <span className="text-blue-600">{finalScore.total.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setShowScoreModal(false)}
                className={`px-6 py-2 rounded-lg font-semibold transition ${isLightMode ? "bg-gray-500 hover:bg-gray-600" : "bg-gray-600 hover:bg-gray-700"} text-white`}
              >
                Close
              </button>
              <button
                onClick={handleNewGameClick}
                className={`px-6 py-2 rounded-lg font-semibold transition ${isLightMode ? "bg-blue-500 hover:bg-blue-600" : "bg-blue-600 hover:bg-blue-700"} text-white`}
              >
                New Game
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Game Confirmation Modal */}
      {showNewGameModal && (
        <div 
          className={`fixed inset-0 ${isLightMode ? "bg-gray-900/40" : "bg-gray-950/60"} backdrop-blur-sm flex items-center justify-center z-50 p-4`}
          onClick={() => setShowNewGameModal(false)}
        >
          <div 
            className={`${bgCard} rounded-lg shadow-xl max-w-md w-full p-6 ${textMain}`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Start New Game?</h2>
              <button
                onClick={() => setShowNewGameModal(false)}
                className={`text-2xl ${textMuted} hover:${textMain} transition`}
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <p className={textMuted}>
                This will start a new game. Your current progress will be lost.
              </p>
              
              <div>
                <label className={`block mb-2 font-semibold ${textMain}`}>
                  Select Difficulty:
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {["random", "easy", "medium", "hard"].map((diff) => (
                    <button
                      key={diff}
                      onClick={() => setSelectedDifficulty(diff)}
                      className={`px-4 py-3 rounded-lg font-semibold transition ${
                        selectedDifficulty === diff
                          ? isLightMode
                            ? "bg-blue-600 text-white"
                            : "bg-blue-500 text-white"
                          : `${bgInput} ${bgInputHover} ${textMain}`
                      }`}
                    >
                      {diff.charAt(0).toUpperCase() + diff.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setShowNewGameModal(false)}
                className={`px-6 py-2 rounded-lg font-semibold transition ${isLightMode ? "bg-gray-500 hover:bg-gray-600" : "bg-gray-600 hover:bg-gray-700"} text-white`}
              >
                Cancel
              </button>
              <button
                onClick={handleNewGameConfirm}
                className={`px-6 py-2 rounded-lg font-semibold transition ${isLightMode ? "bg-blue-500 hover:bg-blue-600" : "bg-blue-600 hover:bg-blue-700"} text-white`}
              >
                Start New Game
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Game;
