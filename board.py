import numpy as np
from copy import deepcopy
COL=7
ROWS=6
moves=[(1,0),(0,1),(1,1),(1,-1)]
AI = 1
HUMAN = 2

def initilize_board():
    board=np.zeros((ROWS, COL), dtype=int)
    return board

def legalmove(board):
    legal=[]
    for c in range(COL):
        if board[0][c]==0:
            legal.append(c)
    return legal
def makemove(board,col,player):
    for r in range(ROWS-1,-1,-1):
        if board[r][col]==0:
            board[r][col]=player
            return r,col,board
    return None  
def movesimulation(board,col,player):
    tempBoard = deepcopy(board)
    res=makemove(tempBoard,col,player)
    if res==None:
        return None
    else:
       r,col,tempBoard=res
    return r,col,tempBoard

def isboardfilled(board):
    for r in range(ROWS):
        for c in range(COL):
            if board[r][c]==0:
                return False
    return True  

def printboard(board):
    for r in range(ROWS):
        for c in range(COL):
            print("|",board[r][c], end="")
        print("|")

                  
            
        
        
    
