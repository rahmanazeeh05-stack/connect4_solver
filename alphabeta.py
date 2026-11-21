import numpy as np
import math
from hurastic import *
from board import *


def minimax(board, depth, k, alpha, beta, currentplayer,root_player,weight):
    opponent = AI2 if root_player == AI1 else AI1
    if isboardfilled(board):
        ai1_player, ai2_player = get_all_windows(board)
        if root_player == AI1:
            return ai1_player[3] - ai2_player[3]

        return ai2_player[3] - ai1_player[3]

    if k == depth:
        ai1_player, ai2_player = get_all_windows(board)
        if root_player == AI1:
          return H(ai1_player, ai2_player, weight)

        return H(ai2_player, ai1_player, weight)
    if currentplayer == root_player:
        return maximizing(
            board, depth, k, alpha, beta,
            root_player, opponent, weight
        )

    else:

        return minimizing(
        board, depth, k, alpha, beta,
        root_player, opponent, weight)

def maximizing(board, depth, k, alpha, beta,root_player,opponent,weight):
    bestscore = -math.inf
    col = legalmove(board)
    for c in col:
        r, c, new_board = movesimulation(board, c, root_player)
        score = minimax(new_board, depth + 1, k, alpha, beta, opponent,root_player,weight)
        bestscore = max(bestscore, score)
        alpha = max(alpha, bestscore)
        if alpha >= beta:
            break
    return bestscore


def minimizing(board, depth, k, alpha, beta,root_player,opponent,weight):
    bestscore = math.inf

    col = legalmove(board)
    for c in col:
        r, c, new_board = movesimulation(board, c, opponent)
        score = minimax(new_board, depth + 1, k, alpha, beta, root_player,root_player,weight)
        bestscore = min(bestscore, score)
        beta = min(beta, bestscore)

        if alpha >= beta:
            break
    return bestscore


def bestmove(board, k,player,weight):
    alpha = -math.inf
    beta = math.inf
    bestscore = -math.inf
    chosencol = None
    columns = legalmove(board)
    
    if not columns:
        return None
    opponent = AI2 if player == AI1 else AI1
    for col in columns:
        r, c, newboard = movesimulation(board, col, player)
        score = minimax(newboard, 1, k, alpha, beta, opponent,player,weight)
        if score > bestscore:
            bestscore = score
            chosencol = c
        alpha = max(bestscore, alpha)
    return chosencol
