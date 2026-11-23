from board import *
from alphabeta import *
from hurastic import *

board=initilize_board()
k=int(input("enter value of k:"))
while not isboardfilled(board):
    printboard(board)
    print("-------------------------")
    ai_turn=bestmove(board,k)
    makemove(board,ai_turn,AI)
    printboard(board)
    print("-------------------------")
    if isboardfilled(board):
        break
    
    human_turn=int(input("choose col:"))
    while human_turn not in legalmove(board):
       human_turn=int(input("invalid col try again:"))
    makemove(board,human_turn,HUMAN)
    printboard(board)
    print("-------------------------")
    
    if isboardfilled(board):
        break

ai_final,human_final=get_all_windows(board)
score=ai_final[3]-human_final[3]
print("human score:", human_final[3])
print("ai score:", ai_final[3])
if score>0:
    print("AI wins")
elif score<0:
    print("HUMAN wins")
else:
    print("draw")