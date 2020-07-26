from chess import *
from game import *
import random

def random_move(board,team):
    threats = list(possible_moves(board,-team))
    maxValue = 0
    pos = (-1,-1)
    for flag,x1,y1,x2,y2 in threats:
        value = pieceValue[abs(on_board(board,x2,y2))]
        if value > maxValue:
            maxValue = value
            pos = (x2,y2)
    if maxValue == 0:
        #print("moving randomly")
        moves = list(possible_moves(board,team))
    else:
        #print("moving with purpose")
        moves = list(possible_moves(board,team,pos))
        if len(moves) == 0:
            moves = list(possible_moves(board,team))
    movesCN = [translateMoveToChessNotation(move) for move in moves]
    #print("options:",movesCN) 
    move = random.choice(moves)
    #return (move[1:3][::-1],move[3:5][::-1]),False
    return (move[1:3],move[3:5]),False
            
pieceValue = {P : 1,
       fP : 1,
       B : 3,
       N : 3,
       R : 5,
       Q : 9,
       empty : 0,
       K : 100}
