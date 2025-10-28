import time
from typing import Tuple
from Algorithms.Util.board import Board
from Algorithms.transposition_table import TranspositionTable, NodeType
from Algorithms.iterative_deepening import evaluate

WIN_SCORE = 10000  # Match the score from iterative_deepening.py

class MinimaxWithTranspositionTable:
    def __init__(self):
        self.transposition_table = TranspositionTable()
        self.nodes_searched = 0
        self.max_depth = 8  # Default depth
        self.time_limit = 2.0  # Default time limit
    
    def make_move(self, board: Board, debug_mode: bool = False) -> Tuple[int, int]:
        """
        Make a move using iterative deepening with transposition table
        Returns: (move, score)
        """
        start_time = time.time()
        self.nodes_searched = 0
        
        # Get valid moves as fallback
        valid_moves = board.legal_moves()
        if not valid_moves:
            return 0, 0  # Should never happen, but safety first
        
        # Check for immediate win
        immediate_win = self._has_immediate_win(board, 1)
        if immediate_win != -1:
            if debug_mode:
                print(f"Immediate win found at column {immediate_win}")
            return immediate_win, WIN_SCORE * self.max_depth
        
        # Check for blocking opponent's immediate win
        opponent_win = self._has_immediate_win(board, -1)
        if opponent_win != -1:
            if debug_mode:
                print(f"Blocking opponent win at column {opponent_win}")
            return opponent_win, -WIN_SCORE * self.max_depth + 1
        
        best_move = valid_moves[0]  # Safe fallback
        best_score = float('-inf')
        
        # Iterative deepening
        for depth in range(1, self.max_depth + 1):
            if self.time_limit and (time.time() - start_time) >= self.time_limit:
                break
                
            try:
                score, move = self.minimax_with_tt(
                    board, depth, float('-inf'), float('inf'), 
                    True, start_time, self.time_limit
                )
                
                if move != -1 and move in valid_moves:  # Valid move found
                    best_move = move
                    best_score = score
                    
                # Early termination for forced wins/losses
                if abs(score) >= WIN_SCORE * depth:
                    break
                    
            except Exception as e:
                if debug_mode:
                    print(f"Error in depth {depth}: {e}")
                break
        
        # Print statistics if in debug mode
        if debug_mode:
            stats = self.transposition_table.get_stats()
            print(f"TT Stats - Nodes: {self.nodes_searched}, Hit Rate: {stats['hit_rate']}, Table Size: {stats['table_size']}")
            print(f"Chosen move: {best_move}, Score: {best_score}")
        
        return best_move, best_score
    
    def minimax_with_tt(self, board: Board, depth: int, alpha: int, beta: int, 
                       maximizing_player: bool, start_time: float, time_limit: float) -> Tuple[int, int]:
        """
        Minimax with transposition table and alpha-beta pruning
        """
        self.nodes_searched += 1
        
        # Check time limit
        if time_limit and (time.time() - start_time) >= time_limit:
            return self._evaluate_position(board), -1
        
        # Check transposition table
        tt_score, tt_move = self.transposition_table.lookup(board, depth, alpha, beta)
        if tt_score is not None:
            # If we have a score but no move, we still need to find a move
            if tt_move is not None and tt_move in board.legal_moves():
                return tt_score, tt_move
            else:
                # Use the score but still need to search for the best move
                pass
        
        # Terminal node checks
        if self._is_winner(board, 1):
            score = WIN_SCORE * depth  # Match iterative_deepening scoring
            self.transposition_table.store(board, score, None, depth, NodeType.EXACT)
            return score, -1
        
        if self._is_winner(board, -1):
            score = -WIN_SCORE * depth  # Match iterative_deepening scoring
            self.transposition_table.store(board, score, None, depth, NodeType.EXACT)
            return score, -1
        
        if board.is_full() or depth == 0:
            score = self._evaluate_position(board)
            self.transposition_table.store(board, score, None, depth, NodeType.EXACT)
            return score, -1
        
        # Get valid moves
        valid_moves = board.legal_moves()
        if not valid_moves:
            return 0, 0  # Draw position
        
        # Improved move ordering
        ordered_moves = []
        
        # 1. Try transposition table move first
        if tt_move is not None and tt_move in valid_moves:
            ordered_moves.append(tt_move)
            valid_moves.remove(tt_move)
        
        # 2. Try center columns first (better in Connect 4)
        center_moves = [3, 2, 4, 1, 5, 0, 6]  # Center-out ordering
        for col in center_moves:
            if col in valid_moves:
                ordered_moves.append(col)
                valid_moves.remove(col)
        
        # 3. Add any remaining moves
        ordered_moves.extend(valid_moves)
        
        best_move = ordered_moves[0]  # Always have a valid fallback
        original_alpha = alpha
        original_beta = beta
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in ordered_moves:
                # Make move
                row = board.play(move, 1)
                
                # Recursive call
                eval_score, _ = self.minimax_with_tt(board, depth - 1, alpha, beta, 
                                                   False, start_time, time_limit)
                
                # Undo move
                board.undo(move)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            # Store in transposition table
            if max_eval <= original_alpha:
                node_type = NodeType.UPPER_BOUND
            elif max_eval >= original_beta:
                node_type = NodeType.LOWER_BOUND
            else:
                node_type = NodeType.EXACT
            
            self.transposition_table.store(board, max_eval, best_move, depth, node_type)
            return max_eval, best_move
        
        else:  # Minimizing player
            min_eval = float('inf')
            for move in ordered_moves:
                # Make move
                row = board.play(move, -1)
                
                # Recursive call
                eval_score, _ = self.minimax_with_tt(board, depth - 1, alpha, beta, 
                                                   True, start_time, time_limit)
                
                # Undo move
                board.undo(move)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            # Store in transposition table
            if min_eval <= original_alpha:
                node_type = NodeType.UPPER_BOUND
            elif min_eval >= original_beta:
                node_type = NodeType.LOWER_BOUND
            else:
                node_type = NodeType.EXACT
            
            self.transposition_table.store(board, min_eval, best_move, depth, node_type)
            return min_eval, best_move
    
    def _evaluate_position(self, board: Board) -> int:
        """Evaluate the current board position using the same evaluation as iterative_deepening"""
        return evaluate(board)
    
    def _is_winner(self, board: Board, player: int) -> bool:
        """Check if the given player has won the game"""
        # More efficient: check only positions that could be winning
        for row in range(6):  # ROWS
            for col in range(7):  # COLS
                if board.grid[row][col] == player:
                    if board.is_win_at(row, col):
                        return True
        return False
    
    def _has_immediate_win(self, board: Board, player: int) -> int:
        """Check if player has an immediate winning move. Returns column or -1."""
        for col in board.legal_moves():
            row = board.play(col, player)
            if board.is_win_at(row, col):
                board.undo(col)
                return col
            board.undo(col)
        return -1
    
    def get_statistics(self) -> dict:
        """Get search and transposition table statistics"""
        tt_stats = self.transposition_table.get_stats()
        tt_stats["nodes_searched"] = self.nodes_searched
        return tt_stats
    
    def clear_stats(self):
        """Clear statistics"""
        self.nodes_searched = 0
        self.transposition_table.clear()