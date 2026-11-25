from src.board import *
from src.alphabeta import *
from src.hurastic import *
from src.tree import *

board = initilize_board()
k = int(input("enter value of k:"))
while k < 1:
    k = int(input("enter a value >=1 for k"))
while not isboardfilled(board):
    printboard(board)
    print("-------------------------")
    ai_turn, tree = bestmove(board, k)
    print("---------- MINIMAX TREE ---------")
    print_tree(tree)
    print("------------------------------")
    if ai_turn is None:
        break
    makemove(board, ai_turn, AI)

    printboard(board)
    print("-------------------------")
    if isboardfilled(board):
        break

    human_turn = int(input("choose col 1-7:"))
    human_turn = human_turn - 1
    while human_turn not in legalmove(board):
        human_turn = int(input("invalid col try again:"))
    makemove(board, human_turn, HUMAN)
    printboard(board)
    print("-------------------------")

    if isboardfilled(board):
        break

ai_final, human_final = get_all_windows(board)
score = ai_final[3] - human_final[3]
print("human score:", human_final[3])
print("ai score:", ai_final[3])
if score > 0:
    print("AI wins")
elif score < 0:
    print("HUMAN wins")
else:
    print("draw")
