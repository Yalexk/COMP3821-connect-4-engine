import numpy as np
import decimal

from pettingzoo.classic import connect_four_v3

from Algorithms.Util.board import *
from Algorithms.algorithm_manager import *

MAX_SEARCH_DEPTH = 12        # hard cap for depth (increase later as needed) # intead of 8 for TT
TIME_LIMIT_SEC = 5        # per-move time limit (can set to None to disable) # instead of 2.0 for TT

def test_gamestate(algo: Algorithm_Types, state: str, depth: int):
    algorithm_manager = Algorithm_Manager(False)
    algorithm_manager.set_algorithm(algo, depth, None)

    env = connect_four_v3.env(render_mode=None)  # Disable PettingZoo's rendering - we are using our own pygame gui
    env.reset()
    obs, reward, terminated, truncated, info = env.last()
    i = 0
    for agent in env.agent_iter():
        if i < len(state):
            env.step(int(state[i]) - 1)
            i += 1
        else:
            obs, reward, terminated, truncated, info = env.last()

            mask = obs["action_mask"]
            legal_cols = [i for i, ok in enumerate(mask) if ok]

            # Build internal board from the agent's POV
            b = board_from_obs(obs)

            # Make move based on selected algorithm
            algorithm_manager.make_move(b)
            return algorithm_manager.get_nodes_searched()

def main():
    algo_types = [Algorithm_Types.MINIMAX, Algorithm_Types.ABPRUNING, Algorithm_Types.PVSORT, Algorithm_Types.TTABLE]
    f = open("test_data/Test_L1_R1")
    num_lines = sum(1 for _ in f)
    out = np.zeros((num_lines, len(algo_types)))
    f.close()

    f = open("test_data/Test_L1_R1")
    with open("prune_percent_test.txt", "w") as out:
        i = 0
        for s in f:
            out.write(f"state: {s.split()[0]}\n")
            for algo in algo_types:
                metric = test_gamestate(algo, s.split()[0], 6)
                if metric is None:
                    continue
                out.write(f"\t{algo}: {metric}\n")
            i += 1
            if i > 100:
                break
        f.close()


if __name__ == "__main__":
    main()