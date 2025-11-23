# config_constants.py

# Board parameters
ROWS = 6
COLS = 7
CONNECT_N = 4

# Search parameters
WIN_SCORE = 1000000     # score for a forced win
LOSS_SCORE = -1000000
DRAW_SCORE = 0

# Engine defaults
MAX_DEPTH = 12
TIME_LIMIT = 0.5
TRANSPOSITION_TABLE_SIZE = 1_000_000
