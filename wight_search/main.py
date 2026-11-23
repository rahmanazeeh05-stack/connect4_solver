from board import *
from alphabeta import *
from hurastic import *
import numpy as np

weights1 = np.array([20, 10, 2, 0])
weights2 = np.array([1, 3, 10, 20])

board = initilize_board()
k = int(input("enter value of k:"))
while k < 1:
    k = int(input("k must be >= 1:"))
while not isboardfilled(board):
    printboard(board)
    print("-------------------------")
    ai1_turn = bestmove(board, k, AI1, weights1)
    makemove(board, ai1_turn, AI1)
    printboard(board)
    print("-------------------------")
    if isboardfilled(board):
        break

    ai2_turn = bestmove(board, k, AI2, weights2)
    makemove(board, ai2_turn, AI2)
    printboard(board)
    print("-------------------------")

    if isboardfilled(board):
        break

ai1_final, ai2_final = get_all_windows(board)
score = ai1_final[3] - ai2_final[3]
print("ai2 score:", ai2_final[3])
print("ai1 score:", ai1_final[3])
if score > 0:
    print("AI1 wins")
elif score < 0:
    print("AI2 wins")
else:
    print("draw")
