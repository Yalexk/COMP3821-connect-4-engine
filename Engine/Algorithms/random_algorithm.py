import random
from Engine.Algorithms.algorithm import Algorithm
from Engine.board import Board

class RandomAlgo(Algorithm):
    def __init__(self, depth=0, time=0):
        super().__init__(depth, time)

    def make_move(self, b: Board, is_debug: bool):
        move = random.choice(b.legal_moves())
        if is_debug: print(f"Choosing random move {move} from legal moves {b.legal_moves()}")
        return move, None
