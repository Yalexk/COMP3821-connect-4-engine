from pettingzoo.classic import connect_four_v3
import time

from Algorithms.Util.board import *
from Algorithms.algorithm_manager import *
from Display import (
    create_board,
    print_board,
    handle_pygame_events,
    get_player_move_from_pygame,
    animate_disk_drop,
    animate_computer_move
)

MAX_SEARCH_DEPTH = 12        # hard cap for depth (increase later as needed) # intead of 8 for TT
TIME_LIMIT_SEC = 5        # per-move time limit (can set to None to disable) # instead of 2.0 for TT

# Interface for player to select options before starting game
def select_options() -> tuple[str, int, bool]:
    player_turn = None
    is_debug = None

    valid_bool_input = ["Y", "N", "YES", "NO"]
    vaild_algorithm_input = ["0", "1", "2"]

    # Choose whether the player goes first or second
    first_move_qry = input("Player first move? [y/n]: ").capitalize()
    while first_move_qry not in valid_bool_input:
        first_move_qry = input("Invalid input, try again.\nPlayer first move? [y/n]: ").capitalize()
    if first_move_qry in ["Y", "YES"]:
        player_turn = "player_0"
    else:
        player_turn = "player_1"

    # Choose algorithm to use for the agent
    algorithm_str = "Implemented Algorithms: \n" \
            "0: Random" \
            "\n1: Minimax" \
            "\n2: Alpha-Beta Pruning" \
            "\nSelect an Algorithm: "
    algorithm_id = None
    algorithm_qry = input(algorithm_str)
    while algorithm_qry not in vaild_algorithm_input:
        algorithm_qry = input(
            "Invalid input, try again.\n" + algorithm_str
        )
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

    print("Starting Connect 4 Game...")
    screen, font = create_board()

    env = connect_four_v3.env(render_mode=None)  # Disable PettingZoo's rendering - we are using our own pygame gui
    env.reset()

    # Get initial observation to show empty board
    obs, reward, terminated, truncated, info = env.last()
    print_board(screen, font, obs, None, player_turn)
    print("Welcome to Connect 4! You are playing as yellow, please open the game window to play.")

    for agent in env.agent_iter():
        obs, reward, terminated, truncated, info = env.last()
        if terminated or truncated:
            env.step(None)
            continue

        # Handle pygame events to keep window responsive
        handle_pygame_events()

        if agent == player_turn:
            mask = obs["action_mask"]
            legal_cols = [i for i, ok in enumerate(mask) if ok]
<<<<<<< HEAD
            col = None
            player_input = input(f"Legal columns: {legal_cols}, enter column number: ")
            while player_input not in [str(i) for i in legal_cols]:
                player_input = input(f"Invalid! Choose from {legal_cols}: ")
            col = int(player_input)
            action = col
=======
            action = get_player_move_from_pygame(screen, font, obs, legal_cols, agent, player_turn)
            # Animate the disk drop
            animate_disk_drop(screen, font, obs, action, agent, player_turn)
>>>>>>> main
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

            # Animate computer's move with preview and drop
            animate_computer_move(screen, font, obs, action, agent, player_turn)

        env.step(action)

        # Pause briefly after turn to show the move
        time.sleep(0.5)

    # Show final board with game result
    if reward == 0:
        print_board(screen, font, obs, "Game Over - It's a Tie!", agent, player_turn)
        print("Tie!")
    elif agent == player_turn:
        print_board(screen, font, obs, "Game Over - You Win!", agent, player_turn)
        print("Player Wins!")
    else:
        print_board(screen, font, obs, "Game Over - Computer Wins!", agent, player_turn)
        print("Computer Wins!")

    time.sleep(5)  # Show final message for 5 seconds
    env.close()

if __name__ == "__main__":
    main()