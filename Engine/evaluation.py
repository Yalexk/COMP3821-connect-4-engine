# Engine/evaluation.py

from Engine.board import Board
import numpy as np
import Engine.config_constants as cc

def evaluate(b: Board) -> int:


    """
    score = center_score + sum(4-length_window_score)
    center_score = k * (#my_center_disc - #opp_center_disc)        (center col)
    4-length_window_score = 
     * WIN_SCORE            (#my_disc, #opp_disc, #empty) = (4,0,0)
     * 30                   (#my_disc, #opp_disc, #empty) = (3,0,1)
     * 6                    (#my_disc, #opp_disc, #empty) = (2,0,2)
     * -6                   (#my_disc, #opp_disc, #empty) = (0,2,2)
     * -35                  (#my_disc, #opp_disc, #empty) = (0,3,1)
     * -WIN_SCORE           (#my_disc, #opp_disc, #empty) = (0,4,0)
     * 0                    otherwise
    """
    k = 2 # How important the center is

    score = 0

    center = cc.COLS // 2
    score += k * (np.count_nonzero(b.grid[:, center] == 1) - np.count_nonzero(b.grid[:, center] == -1))
    
    def window_score(window):
        myc = np.count_nonzero(window == 1)
        opc = np.count_nonzero(window == -1)
        empty = 4 - myc - opc

        if myc == 4:
            return cc.WIN_SCORE
        if opc == 4:
            return cc.LOSS_SCORE

        s = 0
        if myc == 3 and empty == 1: s += 30
        if myc == 2 and empty == 2: s += 6
        if opc == 3 and empty == 1: s -= 35
        if opc == 2 and empty == 2: s -= 6
        return s

    # Horizontal
    for r in range(cc.ROWS):
        for c in range(cc.COLS-3):
            score += window_score(b.grid[r, c:c+4])
    # Vertical
    for c in range(cc.COLS):
        for r in range(cc.ROWS-3):
            score += window_score(b.grid[r:r+4, c])
    # Diagonal (\)
    for r in range(cc.ROWS-3):
        for c in range(cc.COLS-3):
            score += window_score(np.array([b.grid[r+i, c+i] for i in range(4)], dtype=np.int8))
    # Diagonal (/)
    for r in range(3, cc.ROWS):
        for c in range(cc.COLS-3):
            score += window_score(np.array([b.grid[r-i, c+i] for i in range(4)], dtype=np.int8))

    return score
