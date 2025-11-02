import hashlib
import hashlib
from enum import Enum
from typing import Optional, Tuple
from Algorithms.Util.board import Board

class NodeType(Enum):
    EXACT = 0      # Exact score
    LOWER_BOUND = 1  # Alpha cutoff (score >= stored value)
    UPPER_BOUND = 2  # Beta cutoff (score <= stored value)

class TranspositionEntry:
    def __init__(self, score: int, best_move: Optional[int], depth: int, node_type: NodeType):
        self.score = score
        self.best_move = best_move
        self.depth = depth
        self.node_type = node_type

class TranspositionTable:
    def __init__(self, max_size: int = 1000000):
        self.table = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _hash_board(self, board: Board) -> str:
        """Create a unique hash for the board position"""
        board_str = ""
        for row in range(6):  # ROWS
            for col in range(7):  # COLS
                piece = board.grid[row][col]
                if piece == 1:
                    board_str += "X"
                elif piece == -1:
                    board_str += "O"
                else:
                    board_str += "."
        
        return hashlib.md5(board_str.encode()).hexdigest()
    
    def store(self, board: Board, score: int, best_move: Optional[int], depth: int, node_type: NodeType):
        """Store position in transposition table"""
        if len(self.table) >= self.max_size:
            # Simple replacement: remove oldest entries
            self._cleanup()
        
        key = self._hash_board(board)
        entry = TranspositionEntry(score, best_move, depth, node_type)
        self.table[key] = entry
    
    def lookup(self, board: Board, depth: int, alpha: int, beta: int) -> Tuple[Optional[int], Optional[int]]:
        """
        Lookup position in transposition table
        Returns: (score, best_move) or (None, None) if not found/not usable
        """
        key = self._hash_board(board)
        
        if key not in self.table:
            self.misses += 1
            return None, None
        
        entry = self.table[key]
        
        # Only use entry if it was searched to at least the same depth
        if entry.depth < depth:
            self.misses += 1
            return None, None
        
        self.hits += 1
        
        # Check if we can use this score based on node type
        if entry.node_type == NodeType.EXACT:
            return entry.score, entry.best_move
        elif entry.node_type == NodeType.LOWER_BOUND and entry.score >= beta:
            return entry.score, entry.best_move
        elif entry.node_type == NodeType.UPPER_BOUND and entry.score <= alpha:
            return entry.score, entry.best_move
        
        # Can't use score, but might be able to use best move for move ordering
        return None, entry.best_move
    
    def _cleanup(self):
        """Remove half of the entries to make room"""
        items = list(self.table.items())
        # Keep the second half (more recent entries)
        self.table = dict(items[len(items)//2:])
    
    def get_stats(self) -> dict:
        """Get statistics about table performance"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "table_size": len(self.table)
        }
    
    def clear(self):
        """Clear the transposition table"""
        self.table.clear()
        self.hits = 0
        self.misses = 0