from enum import Enum
from Engine.search_context import SearchContext
from Engine.search_engine import SearchEngine

from Engine.board import Board
from Engine.evaluation import evaluate
from Engine.Algorithms.random_algorithm import RandomAlgo
from Engine.Algorithms.search_algorithm import SearchAlgo

import Engine.config_constants as cc

class Algorithm_Types(Enum):
    RAND = 0
    MINIMAX = 1
    ABPRUNING = 2
    TTABLE = 3
    ITERDEEP = 4
    ITERDEEPTT = 5
    ITERDEEPMOVEORDER = 6


class Algorithm_Manager:
    def __init__(self, debug):
        self.debug_mode = debug
        self.nodes_searched = 0
        self.current_algorithm = RandomAlgo()

    def set_algorithm(self, type: Algorithm_Types, max_depth, max_time):
        if type == Algorithm_Types.RAND:
            self.current_algorithm = RandomAlgo()
            return

        # Build a fresh search context
        ctx = SearchContext()
        ctx.eval_func = evaluate
        ctx.max_depth = max_depth
        ctx.time_limit = max_time

        # --- configure flags ---
        if type == Algorithm_Types.MINIMAX:
            ctx.use_ab = False
            ctx.use_tt = False
            ctx.use_id = False

        elif type == Algorithm_Types.ABPRUNING:
            ctx.use_ab = True
            ctx.use_tt = False
            ctx.use_id = False

        elif type == Algorithm_Types.TTABLE:
            ctx.use_ab = True
            ctx.use_tt = True
            ctx.use_id = False

        elif type == Algorithm_Types.ITERDEEP:
            ctx.use_ab = True
            ctx.use_tt = False
            ctx.use_id = True

        elif type == Algorithm_Types.ITERDEEPTT:
            ctx.use_ab = True
            ctx.use_tt = True
            ctx.use_id = True

        elif type == Algorithm_Types.ITERDEEPMOVEORDER:
            ctx.use_ab = True
            ctx.use_tt = True
            ctx.use_id = True
            ctx.use_move_ordering = True  # PV ordering + center ordering

        # Attach unified search algorithm
        self.current_algorithm = SearchAlgo(ctx)

    def make_move(self, board: Board):
        self.nodes_searched = 0
        move, score, searched = self.current_algorithm.make_move(board, self.debug_mode)
        self.nodes_searched = searched
        return move, score
    
    def get_nodes_searched(self):
        return self.nodes_searched
