from enum import Enum
from Algorithms.random_algorithm import Random_Algorithm
from Algorithms.minimax_algorithm import Minimax_Algorithm
from Algorithms.algorithm import Algorithm
from Algorithms.Util.board import Board

class Algorithm_Types(Enum):
    RAND = 0
    MINIMAX = 1
    ABPRUNING = 2
    PVSORT = 3
    TTABLE = 4

class Algorithm_Manager:
    debug_mode: bool
    current_algorithm: Algorithm

    def __init__(self, is_debug):
        self.debug_mode = is_debug
        self.current_algorithm = Random_Algorithm(0, 0)

    def set_algorithm(self, type: Algorithm_Types, max_search_depth, max_time_limit):
        if (type == Algorithm_Types.RAND):
            self.current_algorithm = Random_Algorithm(max_search_depth, max_time_limit)
        if (type == Algorithm_Types.MINIMAX):
            self.current_algorithm = Minimax_Algorithm(max_search_depth, max_time_limit)

    def set_evaluation_function():
        pass

    def make_move(self, b: Board) -> tuple[int, int]:
        return self.current_algorithm.make_move(b, self.debug_mode)