import time
import numpy as np
from pettingzoo.classic import connect_four_v3

from Algorithms.Util.board import Board

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

    # shouldn't happen
    if best_move is None:
        legals = b.legal_moves()
        best_move = legals[0] if legals else 0
    return best_move, best_score
