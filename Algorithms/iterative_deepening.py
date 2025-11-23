import time
import numpy as np
from pettingzoo.classic import connect_four_v3

from Algorithms.Util.board import Board

# Basic constants
ROWS = 6
COLS = 7
CONNECT_N = 4

# Iterative deppening settings
MAX_SEARCH_DEPTH = 8
TIME_LIMIT_SEC = 2.0

WIN_SCORE = 10000

# Toggles
PV_ordering = True
def evaluate(b: Board) -> int:
    """
    score = center_score + sum(4-length_window_score)
    center_score = k * (#my_center_disc - #opp_center_disc)        (center col)
    4-length_window_score = 
     * WIN_SCORE            (#my_disc, #opp_disc, #empty) = (4,0,0)
     * 30                   (#my_disc, #opp_disc, #empty) = (3,0,1)
     * 6                    (#my_disc, #opp_disc, #empty) = (2,0,2)
     * -6                   (#my_disc, #opp_disc, #empty) = (0,2,2)
     * -35                  (#my_disc, #opp_disc, #empty) = (0,3,1)
     * -WIN_SCORE           (#my_disc, #opp_disc, #empty) = (0,4,0)
     * 0                    otherwise
    """
    k = 2 # How importent the center is

    score = 0

    center = COLS // 2
    score += k * (np.count_nonzero(b.grid[:, center] == 1) - np.count_nonzero(b.grid[:, center] == -1))
    
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

class TimeUp(Exception):
    """Raised when the per-move time limit is exceeded."""
    pass

def minimax(b: Board, depth: int, player: int, start_time: float, time_limit: float | None, best_move: int = None):
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
        return evaluate(b) * player, None, 1

    legal = b.centre_legal_moves()
    if not legal:
        return 0, None, 0

    best_move = None
    search_total = 0
    if player == 1:
        # Maximizing
        best_score = -10**12
        for col in legal:
            row = b.play(col, 1)
            if b.is_win_at(row, col):
                b.undo(col)
                return WIN_SCORE * depth, col,  search_total + 1 # prefer faster win by depth scaling
            score, m, searched = minimax(b, depth-1, -1, start_time, time_limit)
            search_total += searched
            b.undo(col)
            if score > best_score:
                best_score = score
                best_move = col
        return best_score, best_move, search_total
    else:
        # Minimizing
        best_score = 10**12
        for col in legal:
            row = b.play(col, -1)
            if b.is_win_at(row, col):
                b.undo(col)
                return -WIN_SCORE * depth, col, search_total + 1
            score, m, searched = minimax(b, depth-1, 1, start_time, time_limit)
            search_total += searched
            b.undo(col)
            if score < best_score:
                best_score = score
                best_move = col
        return best_score, best_move, search_total

# Iterative Deepening wrapper 
def iterative_deepening_move(b: Board, max_depth: int, time_limit: float):
    """
    for depth = 1..max_depth:
        run plain minimax to that depth
        remember the best move
        if time runs out: stop and return the current best move, best score

    Returns (the best move (col), the best score)
    """
    start = time.time()
    best_move = None
    best_score = None

    max_searched = 0

    for depth in range(1, max_depth + 1):
        try:
            if PV_ordering:
                score, move, searched = minimax(b, depth, player=1, start_time=start, time_limit=time_limit, best_move=best_move)
            else:
                score, move, searched = minimax(b, depth, player=1, start_time=start, time_limit=time_limit)
            max_searched = max(searched, max_searched)
            if move is not None:
                best_move = move
                best_score = score
            # Optional: early exit if score is a forced win/lose at current depth
            if abs(score) >= WIN_SCORE * depth:
                break
        except TimeUp:
            break

    # shouldn't happen
    if best_move is None:
        legals = b.legal_moves()
        best_move = legals[0] if legals else 0
    return best_move, best_score, max_searched
