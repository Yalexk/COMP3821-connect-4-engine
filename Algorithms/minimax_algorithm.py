from Algorithms.algorithm import Algorithm
from Algorithms.Util.board import Board

from Algorithms.iterative_deepening import iterative_deepening_move

class Minimax_Algorithm(Algorithm):
    max_depth: int
    time_limit: float

    def __init__(self, depth, time):
        self.max_depth = depth
        self.time_limit = time

    # Currently just a wrapper for iterative deepening, 
    def make_move(self, b: Board, is_debug: bool):
        return iterative_deepening_move(b, self.max_depth, self.time_limit)