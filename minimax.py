from pettingzoo.classic import connect_four_v3
import numpy as np
import copy

ROW_COUNT = 6
COLUMN_COUNT = 7

class MinimaxEngine:
    def __init__(self, depth=4):
        self.depth = depth
        self.player = 1  # AI player (player_1)
        self.opponent = -1  # Human player (player_0)
    
    def get_best_move(self, board, mask):
        # Find the best move using minimax algorithm
        valid_moves = [col for col, valid in enumerate(mask) if valid]
        best_score = float('-inf')
        best_move = valid_moves[0]  # Default to first valid move
        
        for col in valid_moves:
            # Make the move
            new_board = self._make_move(board, col, self.player)
            # Get the score for this move
            score = self._minimax(new_board, self.depth - 1, False)
            
            if score > best_score:
                best_score = score
                best_move = col
        
        return best_move
    
    def _minimax(self, board, depth, is_maximizing):
        # Check terminal conditions
        # I used arbitrary numbers for move scoring - can be changed
        if self._is_winning_move(board, self.player):
            return 1000 + depth  # Prefer quicker wins
        if self._is_winning_move(board, self.opponent):
            return -1000 - depth  # Prefer to delay losses
        if self._is_board_full(board) or depth == 0:
            return self._evaluate_position(board)
        
        valid_moves = self._get_valid_moves(board)
        
        if is_maximizing:
            max_score = float('-inf')
            for col in valid_moves:
                new_board = self._make_move(board, col, self.player)
                score = self._minimax(new_board, depth - 1, False)
                max_score = max(max_score, score)
            return max_score
        else:
            min_score = float('inf')
            for col in valid_moves:
                new_board = self._make_move(board, col, self.opponent)
                score = self._minimax(new_board, depth - 1, True)
                min_score = min(min_score, score)
            return min_score
    
    def _make_move(self, board, col, player):
        # Make a move on the board and return new board state
        new_board = copy.deepcopy(board)
        for row in range(ROW_COUNT - 1, -1, -1):
            if new_board[row][col] == 0:
                new_board[row][col] = player
                break
        return new_board
    
    def _get_valid_moves(self, board):
        #Get list of valid column moves
        return [col for col in range(COLUMN_COUNT) if board[0][col] == 0]
    
    def _is_board_full(self, board):
        #Check if board is completely full
        return all(board[0][col] != 0 for col in range(COLUMN_COUNT))
    
    def _is_winning_move(self, board, player):
        # Check if the given player has won
        # Check horizontal
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT - 3):
                if all(board[row][col + i] == player for i in range(4)):
                    return True
        
        # Check vertical
        for row in range(ROW_COUNT - 3):
            for col in range(COLUMN_COUNT):
                if all(board[row + i][col] == player for i in range(4)):
                    return True
        
        # Check diagonal South West direction
        for row in range(ROW_COUNT - 3):
            for col in range(COLUMN_COUNT - 3):
                if all(board[row + i][col + i] == player for i in range(4)):
                    return True
        
        # Check diagonal North East direction
        for row in range(ROW_COUNT - 3):
            for col in range(3, COLUMN_COUNT):
                if all(board[row + i][col - i] == player for i in range(4)):
                    return True
        
        return False
    
    # Evaluates the position based on possible wins, and weights center columns stronger
    def _evaluate_position(self, board):
        # Evaluate the current board position
        score = 0
        
        # Evaluate all possible 4 piece windows
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT - 3):
                window = [board[row][col + i] for i in range(4)]
                score += self._evaluate_window(window)
        
        for row in range(ROW_COUNT - 3):
            for col in range(COLUMN_COUNT):
                window = [board[row + i][col] for i in range(4)]
                score += self._evaluate_window(window)
        
        for row in range(ROW_COUNT - 3):
            for col in range(COLUMN_COUNT - 3):
                window = [board[row + i][col + i] for i in range(4)]
                score += self._evaluate_window(window)
        
        for row in range(ROW_COUNT - 3):
            for col in range(3, COLUMN_COUNT):
                window = [board[row + i][col - i] for i in range(4)]
                score += self._evaluate_window(window)
        
        # Bonus for center column
        center_col = COLUMN_COUNT // 2
        center_count = sum(1 for row in range(ROW_COUNT) if board[row][center_col] == self.player)
        score += center_count * 3
        
        return score
    
    def _evaluate_window(self, window):
        # Evaluate a 4-piece window
        score = 0
        player_count = window.count(self.player)
        opponent_count = window.count(self.opponent)
        empty_count = window.count(0)
        
        if player_count == 4:
            score += 100
        elif player_count == 3 and empty_count == 1:
            score += 10
        elif player_count == 2 and empty_count == 2:
            score += 2
        
        if opponent_count == 3 and empty_count == 1:
            score -= 80  # Block opponent winning moves
        
        return score


env = connect_four_v3.env(render_mode="human")
env.reset()

HUMAN = "player_0"  # You are the first player'
# moves that are made represented as an integer containing 1 - 7 to represent the columns.
moves = []

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

# Initialize the minimax engine - change the depth here, aiming for 42 for complete solve
minimax_engine = MinimaxEngine(depth=6)

for agent in env.agent_iter():
    obs, reward, terminated, truncated, info = env.last()
    if terminated or truncated:
        env.step(None)
        continue

    if agent == HUMAN:
        mask = obs["action_mask"]
        
        legal_cols = [i for i, ok in enumerate(mask) if ok]
        col = int(input(f"Legal columns: {legal_cols}, enter column number: "))
        while col not in legal_cols:
            col = int(input(f"Invalid! Choose from {legal_cols}: "))
        action = col
    else:
        # Use Minimax algorithm to choose the best move
        current_position = "".join(str(m) for m in moves)
        print(f"Current move code before engine move: {current_position}")
        
        # Convert observation to the format of the Minmax engine
        observation = obs["observation"]
        mask = obs["action_mask"]

        # Convert PettingZoo observation into board representation 
            # observation[:, :, 0] represents player_0's pieces  
            # observation[:, :, 1] represents player_1's pieces
        board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)
        board[observation[:, :, 0] == 1] = -1  # player_0 (human) pieces
        board[observation[:, :, 1] == 1] = 1   # player_1 (AI) pieces
        
        converted_board = board
        
        # Get the best move from minimax
        action = minimax_engine.get_best_move(converted_board, mask)
        print(f"Minimax chose column: {action}")

    moves.append(action + 1)
    env.step(action)

env.close()




