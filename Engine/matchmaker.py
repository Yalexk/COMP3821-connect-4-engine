# matchmaker.py
from pettingzoo.classic import connect_four_v3
import time

from Engine.board import *
from Engine.algorithm_manager import *
from Engine.Display import (
    create_board,
    print_board,
    handle_pygame_events,
    animate_computer_move
)

import Engine.config_constants as cc

def ascii_print_board(obs):
    """Print a simple 6x7 ASCII board for AI vs AI."""
    grid = board_from_obs(obs).grid
    symbols = {0: ".", 1: "X", -1: "O"}  # fix: -1 is O

    print("\n  0 1 2 3 4 5 6")
    for row in grid:
        print(" ", " ".join(symbols[v] for v in row))
    print()

def select_options() -> tuple[int, int, bool]:
    ALGORITHM_QUERY_STRING = """Implemented Algorithms:
        0: Random
        1: Minimax
        2: Minimax w AB
        3: Minimax w AB and TT
        4: Minimax w AB and ID
        5: Minimax w AB, ID and TT
        6: Minimax w AB, ID, TT, Move ordering
        Select an Algorithm: """
    
    valid_bool_input = ["Y", "N", "YES", "NO"]
    valid_algorithm_input = ["0", "1", "2", "3", "4", "5", "6"]

    # Choose algorithm for agent_0
    algorithm_qry = input(ALGORITHM_QUERY_STRING)
    while algorithm_qry not in valid_algorithm_input:
        algorithm_qry = input(ALGORITHM_QUERY_STRING)
    id1 = int(algorithm_qry)

    # Choose algorithm for agent_1
    algorithm_qry = input(ALGORITHM_QUERY_STRING)
    while algorithm_qry not in valid_algorithm_input:
        algorithm_qry = input(ALGORITHM_QUERY_STRING)
    id2 = int(algorithm_qry)

    # Debug mode?
    debug_qry = input("Turn on Debug Mode? [y/n]: ").capitalize()
    while debug_qry not in valid_bool_input:
        debug_qry = input("Invalid input, try again.\nTurn on Debug Mode? [y/n]: ").capitalize()
    is_debug = debug_qry in ["Y", "YES"]

    return id1, id2, is_debug


def initialise() -> tuple[Algorithm_Manager, Algorithm_Manager]:
    id1, id2, is_debug = select_options()

    algorithm_manager1 = Algorithm_Manager(is_debug)
    algorithm_manager1.set_algorithm(Algorithm_Types(id1), cc.MAX_DEPTH, cc.TIME_LIMIT)

    algorithm_manager2 = Algorithm_Manager(is_debug)
    algorithm_manager2.set_algorithm(Algorithm_Types(id2), cc.MAX_DEPTH, cc.TIME_LIMIT)

    return algorithm_manager1, algorithm_manager2


def main():
    algorithm_manager1, algorithm_manager2 = initialise()

    print("Starting Matchmaker (AI vs AI, ASCII FAST MODE)...")

    env = connect_four_v3.env(render_mode=None)
    env.reset()

    obs, reward, terminated, truncated, info = env.last()

    for agent in env.agent_iter():
        obs, reward, terminated, truncated, info = env.last()
        
        if terminated or truncated:
            env.step(None)
            continue

        # Determine algorithm
        if agent == "player_0":
            move, score = algorithm_manager1.make_move(board_from_obs(obs))
        else:
            move, score = algorithm_manager2.make_move(board_from_obs(obs))

        mask = obs["action_mask"]
        legal_cols = [i for i, ok in enumerate(mask) if ok]

        # Safety
        if move not in legal_cols:
            move = legal_cols[0]

        env.step(int(move))

    ascii_print_board(obs)


if __name__ == "__main__":
    main()
