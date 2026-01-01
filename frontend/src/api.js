import axios from "axios";

// Base URL for the backend API
const API_URL = "http://127.0.0.1:8000";

/**
 * Fetches a new Sudoku puzzle from the backend API.
 * 
 * @param {string} difficulty - The difficulty level ('easy', 'medium', 'hard', or 'random')
 * @returns {Promise<Object>} An object containing:
 *   - puzzle: 9x9 array with 0s for empty cells
 *   - solution: 9x9 array with the complete solution
 *   - difficulty: The difficulty level
 *   - board_id: The database ID of the board
 */
export const fetchSudoku = async (difficulty = "random") => {
  const response = await axios.get(`${API_URL}/game`, {
    params: { difficulty }
  });
  return response.data;
};
