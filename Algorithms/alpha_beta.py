from collections.abc import Callable

from Algorithms.algorithm import Algorithm
from Algorithms.Util.board import Board
from Algorithms.Util.window_score_eval import evaluate as window_eval

class Alpha_Beta_Algorithm(Algorithm):
    max_depth: int
    time_limit: float
    eval_func: Callable[[Board], int]
    searched_nodes: int

    def __init__(self, depth, time):
        self.max_depth = depth
        self.time_limit = time
        self.eval_func = window_eval
        self.searched_nodes = 0

    def make_move(self, b: Board, is_debug: bool):
        best_move, best_score, n_searched = iterative_deepening_move(b, self.max_depth, self.time_limit, is_debug)
        self.searched_nodes = n_searched
        return best_move, best_score
    
    def set_evaluation_function(self, function: Callable[[Board], int]):
        self.eval_func = function

    def evaluate(self, b: Board):
        return self.eval_func(b)
    
    def get_nodes_searched(self):
        return self.searched_nodes
    
    # Alpha is the highest possible move in siblings (-inf if possibility unknown)
    # Beta is the lowest possible move in siblings (inf if possibility unknown)
    def alpha_beta(self, b: Board, depth: int, player: int, alpha: int, beta: int, start_time: float, time_limit: float | None, debug: bool):
        self.searched_nodes += 1
        # Time control
        if time_limit is not None and (time.time() - start_time) >= time_limit:
            raise TimeUp()

        # Terminal / depth cut
        if depth == 0 or b.is_full():
            return self.evaluate(b) * player, None

        legal = b.legal_moves()
        if not legal:
            return 0, None

        best_move = None
        if player == 1:
            # Maximizing
            # Alpha is the score of the best move for maximiser in the current turn found in children
            # Beta is the score of the  best move for maximiser in the previous turn found in siblings by the minimiser
            best_score = -10**12
            for col in legal:
                row = b.play(col, 1)
                if b.is_win_at(row, col):
                    b.undo(col)
                    return WIN_SCORE * depth, col  # prefer faster win by depth scaling
                score, _ = self.alpha_beta(b, depth-1, -1, alpha, beta, start_time, time_limit, debug)
                b.undo(col)
                if score > best_score:
                    best_score = score
                    best_move = col

                # Set alpha to be the best (maximal) score found within children
                # Alpha is score of the largest move found so far by the maximiser within its children
                #   i.e. the maximiser on this turn has a move that can recive a score of at least alpha.
                # Beta is the largest score the minimiser on the previous turn can guarantee
                #   i.e. the minimiser on the previous turn has a move that causes the maximiser can recieve a score of a most beta.
                # If alpha >= beta, then there exists a move that is better for the minimiser in the previous move,
                #   therefore there is no more reason to check other options from this branch since the minimiser already
                #   knows it has a better move.
                alpha = max(score, alpha)
                if beta <= alpha:
                    if debug:
                        print("pruned at depth: " + str(self.max_depth - depth))
                    break
            return best_score, best_move
        else:
            # Minimizing
            # Alpha is the score of the  best move for minimiser in the previous turn found in siblings by the maximiser
            # Beta is the score of the best move for minimiser in the current turn found in children
            best_score = 10**12
            for col in legal:
                row = b.play(col, -1)
                if b.is_win_at(row, col):
                    b.undo(col)
                    return -WIN_SCORE * depth, col
                score, _ = self.alpha_beta(b, depth-1, 1, alpha, beta, start_time, time_limit, debug)
                b.undo(col)
                if score < best_score:
                    best_score = score
                    best_move = col

                # Set beta to be the best (minimal) score found within children
                # Alpha is the smallest score the maximiser on the previous turn can guarantee
                #   i.e. the maximiser on the previous turn has a move that causes the minimiser can recieve a score of a least alpha.
                # Beta is score of the smallest move found so far by the minimiser within its children
                #   i.e. the minimiser on this turn has a move that can recive a score of at most beta.
                # If alpha >= beta, then there exists a move that is better for the maximiser in the previous move,
                #   therefore there is no more reason to check other options from this branch since the maximiser already
                #   knows it has a better move.
                beta = min(score, beta)
                if beta <= alpha:
                    if debug:
                        print("pruned at depth: " + str(self.max_depth - depth))
                    break
                
            return best_score, best_move
    
import time

from Algorithms.Util.board import Board

# Basic constants
ROWS = 6
COLS = 7
CONNECT_N = 4

# Iterative deepening settings
MAX_SEARCH_DEPTH = 8        # hard cap for depth (increase later as needed)
TIME_LIMIT_SEC = 2.0        # per-move time limit (can set to None to disable)

WIN_SCORE = 10_000          # terminal win/lose magnitude

class TimeUp(Exception):
    """Raised when the per-move time limit is exceeded."""
    pass

# Iterative Deepening wrapper from iterative deepening: should make this modular in the future
def iterative_deepening_move(b: Board, max_depth: int, time_limit: float, debug: bool):
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
        searched_nodes = 0
        try:
            abalgo = Alpha_Beta_Algorithm(max_depth, time_limit)
            abalgo.searched_nodes = 0
            score, move = abalgo.alpha_beta(b, depth, 1, -10**12, 10**12, start_time=start, time_limit=time_limit, debug=debug)
            if move is not None:
                best_move = move
                best_score = score
            # Optional: early exit if score is a forced win/lose at current depth
            searched_nodes = abalgo.get_nodes_searched()
            if abs(score) >= WIN_SCORE * depth:
                break
        except TimeUp:
            break

    # Fallback in case nothing was found (shouldn't happen): pick first legal
    if best_move is None:
        legals = b.legal_moves()
        best_move = legals[0] if legals else 0
    return best_move, best_score, searched_nodes