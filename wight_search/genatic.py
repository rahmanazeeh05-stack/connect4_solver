import numpy as np
from board import *
from alphabeta import *
from hurastic import *
AI1=1
AI2=2


def genrate_population(size, num_dim):
    population = np.random.uniform(1, 100, size=(size, num_dim))
    population = np.sort(population, axis=1)
    return population


def fitness(win, draw, size):
    return (win + 0.5 * draw) / size ** 2



def tournament(population, size):
    pass


def gameStats(weights,k):
    n=len(weights)
    status=[[0,0]]
    for i in range (n):
        for j in range(i+1,n):
            if i==j:
                continue

            board = initilize_board()
            while not isboardfilled(board):
   
              ai1_turn = bestmove(board, k, AI1, weights[i])
              makemove(board, ai1_turn, AI1)
    
              if isboardfilled(board):
                 break

              ai2_turn = bestmove(board, k, AI2, weights[j])
              makemove(board, ai2_turn, AI2)
    

              if isboardfilled(board):
                     break

            ai1_final, ai2_final = get_all_windows(board)
            score = ai1_final[3] - ai2_final[3]

            if score > 0:
                status[i][0]+=1
    
            elif score < 0:
                status[j][1] +=1
             
            else:
              status[i][1] +=1
              status[j][1] +=1
    return status          
