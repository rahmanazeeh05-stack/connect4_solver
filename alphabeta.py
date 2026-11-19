import numpy as np
import math
from hurastic import *
from board import *

AI = 1
HUMAN = 2
def minimax(board,depth,k,alpha,beta,mx_player):
    if isboardfilled(board):
        ai_player,human_player=get_all_windows(board)
        return ai_player[3]-human_player[3]
    if k==depth:
        ai_player,human_player=get_all_windows(board)
        return H(ai_player,human_player)
    if mx_player:
        
        return maximizing(board, depth, k, alpha, beta)
    else:
       
        return minimizing(board, depth, k, alpha, beta)
        

def maximizing(board,depth,k,alpha,beta):
    bestscore=-math.inf  
    col=legalmove(board)
    for c in col:
          r,c,new_board=movesimulation(board,c,AI)
          score=minimax(new_board,depth+1,k,alpha,beta,False)
          bestscore=max(bestscore,score)
          alpha=max(alpha,bestscore) 
          if alpha>=beta:
              break
    return bestscore  

def minimizing(board,depth,k,alpha,beta):
    bestscore=math.inf
    
    col=legalmove(board)
    for c in col:
        r,c,new_board=movesimulation(board,c,HUMAN)
        score=minimax(new_board,depth+1,k,alpha,beta,True)
        bestscore=min(bestscore,score)
        beta=min(beta,bestscore)
        
        if alpha>=beta:
            break
    return bestscore    

def bestmove(board,k):
    alpha=-math.inf
    beta=math.inf
    bestscore=-math.inf
    chosencol=None
    columns=legalmove(board)
    if not columns:
        return None
    for col in columns:
        r,c,newboard=movesimulation(board,col,AI)
        score=minimax(newboard,1,k,alpha,beta,False)
        if score>bestscore:
            bestscore=score
            chosencol=c
        alpha=max(bestscore,alpha)
    return chosencol
    