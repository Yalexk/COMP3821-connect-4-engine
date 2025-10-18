from pettingzoo.classic import connect_four_v3

from Algorithms.Util.board import *
from Algorithms.algorithm_manager import *

MAX_SEARCH_DEPTH = 8        # hard cap for depth (increase later as needed)
TIME_LIMIT_SEC = 2.0        # per-move time limit (can set to None to disable)

# Interface for player to select options before starting game
def select_options() -> tuple[str, int, bool]:
    player_turn = None
    is_debug = None

    valid_bool_input = ["Y", "N", "YES", "NO"]
    vaild_algorithm_input = ["0", "1"]

    # Choose whether the player goes first or second
    first_move_qry = input("Player first move? [y/n]: ").capitalize()
    while first_move_qry not in valid_bool_input:
        first_move_qry = input("Invalid input, try again.\nPlayer first move? [y/n]: ").capitalize()
    if first_move_qry in ["Y", "YES"]:
        player_turn = "player_0"
    else:
        player_turn = "player_1"
    
    # Choose algorithm to use for the agent
    algorithm_id = None
    algorithm_qry = input("Implemented Algorithms: \n0: Random\n1: Minimax\nSelect an Algorithm: ")
    while algorithm_qry not in vaild_algorithm_input:
        algorithm_qry = input("Invalid input, try again.\nImplemented Algorithms: \n0: Random\n1: Minimax\nSelect an Algorithm: ")
    algorithm_id = int(algorithm_qry)

    # Choose whether algorithms should be run in debug mode
    debug_qry = input("Turn on Debug Mode? [y/n]: ").capitalize()
    while debug_qry not in valid_bool_input:
        debug_qry = input("Invalid input, try again.\nTurn on Debug Mode? [y/n]\n").capitalize()
    if debug_qry in ["Y", "YES"]:
        is_debug = True
    else:
        is_debug = False
    
    return player_turn, algorithm_id, is_debug

# Creates an Algorithm Manager object and returns player first or second
# select_options can be replaced for set conditions when testing
def initialise() -> tuple[str, Algorithm_Manager]:
    player_turn, algorithm_id, is_debug = select_options()

    algorithm_manager = Algorithm_Manager(is_debug)
    algorithm_manager.set_algorithm(Algorithm_Types(algorithm_id), MAX_SEARCH_DEPTH, TIME_LIMIT_SEC)

    return player_turn, algorithm_manager

def main():
    player_turn, algorithm_manager = initialise()
    
    env = connect_four_v3.env(render_mode="human")
    env.reset()

    for agent in env.agent_iter():
        obs, reward, terminated, truncated, info = env.last()
        if terminated or truncated:
            env.step(None)
            continue

        if agent == player_turn:
            mask = obs["action_mask"]
            legal_cols = [i for i, ok in enumerate(mask) if ok]
            col = None
            player_input = input(f"Legal columns: {legal_cols}, enter column number: ")
            while player_input not in ["0", "1", "2", "3", "4", "5", "6"]:
                player_input = input(f"Invalid! Choose from {legal_cols}: ")
            col = int(player_input)
            while col not in legal_cols:
                player_input = input(f"Invalid! Choose from {legal_cols}: ")
                while player_input not in ["0", "1", "2", "3", "4", "5", "6"]:
                    player_input = input(f"Invalid! Choose from {legal_cols}: ")
            action = col
        else:
            mask = obs["action_mask"]
            legal_cols = [i for i, ok in enumerate(mask) if ok]

            # Build internal board from the agent's POV
            b = board_from_obs(obs)

            # Make move based on selected algorithm
            move, score = algorithm_manager.make_move(b)

            # Safety: ensure move is legal according to the env mask
            if move not in legal_cols:
                move = legal_cols[0]

            action = int(move)

        env.step(action)

    if reward == 0:
        print("Tie!")
    elif agent == player_turn:
        print("Player Wins!")
    else:
        print("Computer Wins!")

    env.close()

if __name__ == "__main__":
    main()