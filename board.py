import numpy as np
from copy import deepcopy
from hurastic import *




def initilize_board():
    board = np.zeros((ROWS, COLS), dtype=int)
    return board


def legalmove(board):
    """gets list of columns that still aren't full and legal to make a move in"""
    legal = []
    for c in range(COLS):
        if board[0][c] == 0:
            legal.append(c)
    return legal


def makemove(board, col, player):
    """
    for a given col loop on rows down to up to know exactly 
    where the row the piece would be placed in
    """
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == 0:
            board[r][col] = player
            return r, col, board
    return None


def movesimulation(board, col, player):
    """applies the move on a copied board (used later to determine the best move)"""
    tempBoard = deepcopy(board)
    res = makemove(tempBoard, col, player)
    if res == None:
        return None
    else:
        r, col, tempBoard = res
    return r, col, tempBoard


def isboardfilled(board):
    """checks if board is full (used later to calc final score)"""
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 0:
                return False
    return True


def printboard(board):
    """prints the board in terminal"""
    for r in range(ROWS):
        for c in range(COLS):
            print("|", board[r][c], end="")
        print("|")
