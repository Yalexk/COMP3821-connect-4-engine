import numpy as np

from Algorithms.Util.board import Board

# Basic constants
ROWS = 6
COLS = 7

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
