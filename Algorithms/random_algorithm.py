import random
from Algorithms.algorithm import Algorithm
from Algorithms.Util.board import Board

class Random_Algorithm(Algorithm):
    def make_move(self, b: Board, is_debug: bool):
        move = random.choice(b.legal_moves())
        if is_debug: print(f"Choosing random move {move} from legal moves {b.legal_moves()}")
        return move, None