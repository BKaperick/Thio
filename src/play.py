from chess import *
import random

def random_move(board,team):
    threats = list(possible_moves(board,-team))
    maxValue = 0
    pos = (-1,-1)
    for flag,x,y in threats:
        value = pieceValue[abs(on_board(board,x,y))]
        if value > maxValue:
            maxValue = value
            pos = (x,y)
    if maxValue == 0:
        moves = list(possible_moves(board,team))
    else:
        moves = list(possible_moves(board,team,pos))
    
    movesCN = [translateMoveToChessNotation(move) for move in moves]
    print("options:",movesCN)
    return random.choice(moves)
            
        
        

pieceValue = {P : 1,
       fP : 1,
       B : 3,
       N : 3,
       R : 5,
       Q : 9,
       empty : 0,
       K : 100}



# Create new human-vs-computer game with the computer as black, using `random_move` to make its moves
game = Game(Bl, random_move)

game.runGame()
