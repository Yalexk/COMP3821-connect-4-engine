from enum import Enum
from Algorithms.random_algorithm import Random_Algorithm
from Algorithms.minimax_algorithm import Minimax_Algorithm
from Algorithms.alpha_beta import Alpha_Beta_Algorithm
from Algorithms.algorithm import Algorithm
from Algorithms.Util.board import Board
from Algorithms.minimax_tt import MinimaxWithTranspositionTable

class Algorithm_Types(Enum):
    RAND = 0
    MINIMAX = 1
    TTABLE = 2
    ABPRUNING = 3
    PVSORT = 4

class Algorithm_Manager:
    debug_mode: bool
    current_algorithm: Algorithm

    def __init__(self, is_debug):
        self.debug_mode = is_debug
        self.current_algorithm = Random_Algorithm(0, 0)
        self.minimax_tt = MinimaxWithTranspositionTable()

    def set_algorithm(self, type: Algorithm_Types, max_search_depth, max_time_limit):
        if (type == Algorithm_Types.RAND):
            self.current_algorithm = Random_Algorithm(max_search_depth, max_time_limit)
        elif (type == Algorithm_Types.MINIMAX):
            self.current_algorithm = Minimax_Algorithm(max_search_depth, max_time_limit)
        elif (type == Algorithm_Types.ABPRUNING):
            self.current_algorithm = Alpha_Beta_Algorithm(max_search_depth, max_time_limit)
        elif type == Algorithm_Types.TTABLE:
            self.current_algorithm = self.minimax_tt
            # Configure the transposition table algorithm with depth and time limit
            self.minimax_tt.max_depth = max_search_depth
            self.minimax_tt.time_limit = max_time_limit

    def set_evaluation_function():
        pass

    def make_move(self, b: Board) -> tuple[int, int]:
        return self.current_algorithm.make_move(b, self.debug_mode)
    
    def get_nodes_searched(self):
        return self.current_algorithm.get_nodes_searched()