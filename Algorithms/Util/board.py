import numpy as np

ROWS = 6
COLS = 7
CONNECT_N = 4

class Board:
    """
    Minimal board for search.
    Representation:
      1  = current player (maximizer)
     -1  = opponent
      0  = empty
    """
    def __init__(self, grid=None):
        self.grid = np.zeros((ROWS, COLS), dtype=np.int8) if grid is None else grid.copy()
        # Precompute current heights in each column (how many pieces already placed)
        self.heights = np.array([np.count_nonzero(self.grid[:, c]) for c in range(COLS)], dtype=np.int8)

    def legal_moves(self):
        """Return list of legal columns in natural order (no move ordering)."""
        return [c for c in range(COLS) if self.heights[c] < ROWS]

    def centre_legal_moves(self):
        """Return list of legal columns going out from centre. (centre ordering)."""
        # It may be more beneficial to have a right-first centre ordering in some cases
        centre_order = [3, 2, 4, 1, 5, 0, 6] 
        return [c for c in centre_order if self.heights[c] < ROWS]

    def play(self, col, player):
        """Drop a disc for 'player' (1 or -1). Return the row index used."""
        r = ROWS - 1 - self.heights[col]
        self.grid[r, col] = player
        self.heights[col] += 1
        return r

    def undo(self, col):
        """Undo last move in the given column."""
        if self.heights[col] == 0:
            return
        r = ROWS - self.heights[col]
        self.grid[r, col] = 0
        self.heights[col] -= 1

    def is_full(self):
        """Check whether board is full (draw if no winner)."""
        return all(self.heights[c] == ROWS for c in range(COLS))

    def is_win_at(self, row, col):
        """Check 4-in-a-row for the stone at (row, col)."""
        player = self.grid[row, col]
        if player == 0:
            return False
        dirs = [(0,1),(1,0),(1,1),(1,-1)]
        for dr, dc in dirs:
            count = 1
            # forward
            rr, cc = row+dr, col+dc
            while 0 <= rr < ROWS and 0 <= cc < COLS and self.grid[rr, cc] == player:
                count += 1
                rr += dr; cc += dc
            # backward
            rr, cc = row-dr, col-dc
            while 0 <= rr < ROWS and 0 <= cc < COLS and self.grid[rr, cc] == player:
                count += 1
                rr -= dr; cc -= dc
            if count >= CONNECT_N:
                return True
        return False

# Convert PettingZoo obs -> Board
def board_from_obs(obs):
    """
    PettingZoo observation planes are (6,7,2): [current_player, other_player].
    We map them to 1 / -1 from the perspective of the agent whose turn it is.
    """
    planes = obs["observation"]
    my_plane = planes[:, :, 0]
    opp_plane = planes[:, :, 1]
    grid = np.zeros((ROWS, COLS), dtype=np.int8)
    grid[my_plane == 1] = 1
    grid[opp_plane == 1] = -1
    return Board(grid)
