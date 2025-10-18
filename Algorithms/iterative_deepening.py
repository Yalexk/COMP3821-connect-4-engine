import time
import numpy as np
from pettingzoo.classic import connect_four_v3

from Algorithms.Util.board import Board

# Basic constants
ROWS = 6
COLS = 7
CONNECT_N = 4

# Iterative deepening settings
MAX_SEARCH_DEPTH = 8        # hard cap for depth (increase later as needed)
TIME_LIMIT_SEC = 2.0        # per-move time limit (can set to None to disable)

WIN_SCORE = 10_000          # terminal win/lose magnitude

# Simple evaluation function
def evaluate(b: Board) -> int:
    """
    Heuristic from the perspective of the side to move (= +1):
    - Mild center column preference.
    - Window scoring over all length-4 slices (horizontal/vertical/diagonals).
    This is intentionally simple for a baseline.
    """
    score = 0

    # Center column preference
    center = COLS // 2
    score += 2 * (np.count_nonzero(b.grid[:, center] == 1) - np.count_nonzero(b.grid[:, center] == -1))

    def window_score(window):
        myc = np.count_nonzero(window == 1)
        opc = np.count_nonzero(window == -1)
        empty = 4 - myc - opc

        if myc == 4:
            return WIN_SCORE
        if opc == 4:
            return -WIN_SCORE

        s = 0
        if myc == 3 and empty == 1: s += 30
        if myc == 2 and empty == 2: s += 6
        if opc == 3 and empty == 1: s -= 35
        if opc == 2 and empty == 2: s -= 6
        return s

    # Horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            score += window_score(b.grid[r, c:c+4])
    # Vertical
    for c in range(COLS):
        for r in range(ROWS-3):
            score += window_score(b.grid[r:r+4, c])
    # Diagonal (\)
    for r in range(ROWS-3):
        for c in range(COLS-3):
            score += window_score(np.array([b.grid[r+i, c+i] for i in range(4)], dtype=np.int8))
    # Diagonal (/)
    for r in range(3, ROWS):
        for c in range(COLS-3):
            score += window_score(np.array([b.grid[r-i, c+i] for i in range(4)], dtype=np.int8))

    return score

# Plain Minimax (no alpha-beta)
class TimeUp(Exception):
    """Raised when the per-move time limit is exceeded."""
    pass

def minimax(b: Board, depth: int, player: int, start_time: float, time_limit: float | None):
    """
    Very simple minimax:
      - 'player' is +1 for side to move, -1 for opponent.
      - No alpha-beta pruning, no transposition table, no move ordering.
      - Time check at each entry to allow iterative deepening to stop cleanly.
    Returns (score, best_move).
    """
    # Time control
    if time_limit is not None and (time.time() - start_time) >= time_limit:
        raise TimeUp()

    # Terminal / depth cut
    if depth == 0 or b.is_full():
        return evaluate(b) * player, None

    legal = b.legal_moves()
    if not legal:
        return 0, None

    best_move = None
    if player == 1:
        # Maximizing
        best_score = -10**12
        for col in legal:
            row = b.play(col, 1)
            if b.is_win_at(row, col):
                b.undo(col)
                return WIN_SCORE * depth, col  # prefer faster win by depth scaling
            score, _ = minimax(b, depth-1, -1, start_time, time_limit)
            b.undo(col)
            if score > best_score:
                best_score = score
                best_move = col
        return best_score, best_move
    else:
        # Minimizing
        best_score = 10**12
        for col in legal:
            row = b.play(col, -1)
            if b.is_win_at(row, col):
                b.undo(col)
                return -WIN_SCORE * depth, col
            score, _ = minimax(b, depth-1, 1, start_time, time_limit)
            b.undo(col)
            if score < best_score:
                best_score = score
                best_move = col
        return best_score, best_move

# Iterative Deepening wrapper
def iterative_deepening_move(b: Board, max_depth: int, time_limit: float):
    """
    Basic Iterative Deepening:
      for depth = 1..max_depth:
        run plain minimax to that depth
        remember the best move
        stop if time runs out (return last completed depth's move)

    Returns chosen move (column index).
    """
    start = time.time()
    best_move = None
    best_score = None

    for depth in range(1, max_depth + 1):
        try:
            score, move = minimax(b, depth, player=1, start_time=start, time_limit=time_limit)
            if move is not None:
                best_move = move
                best_score = score
            # Optional: early exit if score is a forced win/lose at current depth
            if abs(score) >= WIN_SCORE * depth:
                break
        except TimeUp:
            break

    # Fallback in case nothing was found (shouldn't happen): pick first legal
    if best_move is None:
        legals = b.legal_moves()
        best_move = legals[0] if legals else 0
    return best_move, best_score