from Engine.search_engine import SearchEngine
from Engine.search_context import SearchContext

class SearchAlgo:
    def __init__(self, ctx: SearchContext):
        self.engine = SearchEngine()
        self.ctx = ctx

    def make_move(self, board, debug):
        return self.engine.make_move(board, self.ctx)
