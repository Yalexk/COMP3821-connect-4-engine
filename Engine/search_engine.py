from Engine.search_context import SearchContext
from Engine.board import Board
from Engine.transposition_table import NodeType
import Engine.config_constants as cc

# Algorithms/search_engine.py
class SearchEngine:
    def make_move(self, board: Board, ctx: SearchContext):
        ctx.start_timer()
        if ctx.use_id:
            return self.iterative_deepening(board, ctx)
        else:
            return self.search_root(board, ctx.max_depth, ctx)

    # ---------------------------------------------------
    # ROOT SEARCH
    # ---------------------------------------------------
    def search_root(self, board: Board, depth: int, ctx: SearchContext):
        best_move = None
        best_score = float('-inf')

        moves = board.legal_moves()
        if ctx.use_move_ordering:
            moves = self.order_moves(board, moves)

        for m in moves:
            board.play(m, 1)
            score = self.search(board, depth - 1, -10**9, 10**9, False, ctx)
            board.undo(m)

            if score > best_score:
                best_score = score
                best_move = m

            if ctx.time_exceeded():
                break

        # Store PV move at root
        if ctx.use_tt and best_move is not None:
            ctx.tt.store(board, best_score, best_move, depth, NodeType.EXACT)

        return best_move, best_score

    # ---------------------------------------------------
    # CORE SEARCH (Minimax / AB / TT / PV)
    # ---------------------------------------------------
    def search(self, board: Board, depth, alpha, beta, maximizing, ctx: SearchContext):
        alpha_original = alpha
        if ctx.time_exceeded():
            return 0

        # Terminal or leaf
        if depth == 0 or board.is_terminal():
            return ctx.eval_func(board)

        # -------------------------
        # Transposition Table Lookup
        # -------------------------
        tt_move = None
        if ctx.use_tt:
            score, tt_move = ctx.tt.lookup(board, depth, alpha, beta)
            if score is not None:
                return score  # exact score usable

        # -------------------------
        # Move Generation & PV Ordering
        # -------------------------
        moves = board.legal_moves()

        # Try TT/PV move first
        if ctx.use_move_ordering and tt_move is not None and tt_move in moves:
            moves.remove(tt_move)
            moves.insert(0, tt_move)
        # Fallback to center-first
        elif ctx.use_move_ordering:
            moves = self.order_moves(board, moves)

        best_move = None

        # -------------------------
        # Recursive Minimax with AB
        # -------------------------
        if maximizing:
            value = -10**9
            for m in moves:
                board.play(m, 1)
                score = self.search(board, depth - 1, alpha, beta, False, ctx)
                board.undo(m)

                if score > value:
                    value = score
                    best_move = m

                if ctx.use_ab:
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break
        else:
            value = 10**9
            for m in moves:
                board.play(m, -1)
                score = self.search(board, depth - 1, alpha, beta, True, ctx)
                board.undo(m)

                if score < value:
                    value = score
                    best_move = m

                if ctx.use_ab:
                    beta = min(beta, value)
                    if beta <= alpha:
                        break

        # -------------------------
        # Store PV Move in TT
        # -------------------------
        if ctx.use_tt and best_move is not None:
            if value <= alpha_original:
                node_type = NodeType.UPPER_BOUND
            elif value >= beta:
                node_type = NodeType.LOWER_BOUND
            else:
                node_type = NodeType.EXACT

            ctx.tt.store(board, value, best_move, depth, node_type)

        return value

    # ---------------------------------------------------
    # ITERATIVE DEEPENING
    # ---------------------------------------------------
    def iterative_deepening(self, board: Board, ctx: SearchContext):
        best_move = None
        ctx.tt.clear()  # clear TT to store fresh PV moves

        for d in range(1, ctx.max_depth + 1):
            move, _ = self.search_root(board, d, ctx)
            if ctx.time_exceeded():
                break
            if move is not None:
                best_move = move  # best PV move so far

        return best_move, 0

    # ---------------------------------------------------
    # Move Ordering: center-first
    # ---------------------------------------------------
    def order_moves(self, board: Board, moves):
        center = cc.COLS // 2
        return sorted(moves, key=lambda m: abs(m - center))

