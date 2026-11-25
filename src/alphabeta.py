import numpy as np
import math
from .hurastic import *
from .board import *
from .tree import *


def minimax(board, depth, k, alpha, beta, mx_player, node):
    if isboardfilled(board):
        ai_player, human_player = get_all_windows(board)
        node.value = ai_player[3] - human_player[3]
        node.is_leaf = True
        return node.value
    if k == depth:
        ai_player, human_player = get_all_windows(board)
        node.value = H(ai_player, human_player)
        node.is_leaf = True

        return node.value
    if mx_player:

        return maximizing(board, depth, k, alpha, beta, node)
    else:

        return minimizing(board, depth, k, alpha, beta, node)


def maximizing(board, depth, k, alpha, beta, node):
    bestscore = -math.inf
    col = legalmove(board)
    for c in col:
        result = movesimulation(board, c, AI)
        if not result:
            continue
        r, c_chosen, new_board = result
        child = Node(new_board, depth + 1, AI, c)
        node.children.append(child)

        score = minimax(new_board, depth + 1, k, alpha, beta, False, child)
        bestscore = max(bestscore, score)
        alpha = max(alpha, bestscore)
        if alpha >= beta:
            node.cutoff = True
            break
    node.value = bestscore
    return bestscore


def minimizing(board, depth, k, alpha, beta, node):
    bestscore = math.inf

    col = legalmove(board)
    for c in col:

        result = movesimulation(board, c, HUMAN)
        if not result:
            continue
        r, c_chosen, new_board = result
        child = Node(new_board, depth + 1, HUMAN, c)

        node.children.append(child)
        score = minimax(new_board, depth + 1, k, alpha, beta, True, child)
        bestscore = min(bestscore, score)
        beta = min(beta, bestscore)

        if alpha >= beta:
            node.cutoff = True
            break
    node.value = bestscore
    return bestscore


def bestmove(board, k):
    alpha = -math.inf
    beta = math.inf
    bestscore = -math.inf
    chosencol = None
    root = Node(board, 0, None)
    columns = legalmove(board)
    if not columns:
        return None, root
    for col in columns:

        r, c, newboard = movesimulation(board, col, AI)
        child = Node(newboard, 1, AI, col)
        root.children.append(child)
        score = minimax(newboard, 1, k, alpha, beta, False, child)
        if score > bestscore:
            bestscore = score
            chosencol = c
        alpha = max(bestscore, alpha)
        root.value = bestscore
    return chosencol, root
