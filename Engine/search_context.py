import time
from dataclasses import dataclass
from Engine.transposition_table import TranspositionTable
import Engine.config_constants as cc

@dataclass
class SearchContext:
    max_depth: int = cc.MAX_DEPTH
    time_limit: float = cc.TIME_LIMIT
    eval_func: callable = None

    use_ab: bool = True
    use_tt: bool = True
    use_id: bool = True
    use_move_ordering: bool = True

    tt: TranspositionTable = None
    start: float = None

    def __post_init__(self):
        self.tt = TranspositionTable()
        self.start = None

    def start_timer(self):
        self.start = time.time()

    def time_exceeded(self):
        if self.time_limit is None:
            return False
        if self.start is None:
            return False
        return (time.time() - self.start) >= self.time_limit
