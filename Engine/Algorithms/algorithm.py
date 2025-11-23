from Engine.board import Board

# Interface for algorithms:
class Algorithm:
    # depth, time: maximum depth and time limit in iterative deepening search
    def __init__(self, depth, time):
        pass

    # use this function for choosing moves
    # is_debug: will be true when in debug mode, use to help in debugging
    # returns tuple of (move, score)
    def make_move(self, b: Board, is_debug: bool) -> tuple[int, int | None]:
        pass
