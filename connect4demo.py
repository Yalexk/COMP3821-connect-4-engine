from pettingzoo.classic import connect_four_v3
import numpy as np
env = connect_four_v3.env(render_mode="human")
env.reset()

HUMAN = "player_0"  # You are the first player'
# moves that are made represented as an integer containing 1 - 7 to represent the columns.
moves = []

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
        # Replace this later with your Minimax or MCTS
        current_position = "".join(str(m) for m in moves)
        print(f"Current move code before engine move: {current_position}")
        
        mask = obs["action_mask"]
        action = env.action_space(agent).sample(mask)

    moves.append(action + 1)
    env.step(action)

env.close()


