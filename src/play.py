from chess import *
from game import *
import random

def random_move(board,team):
    print("SCORE:",score_board(board,team))
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

    # choose move which maximizes minimum score in follow-up
    minscores = []
    for move in moves:
        # board after my proposed move
        local = hypothetical_board(board,move)
        # possible responses
        threats = possible_moves(local,-team)
        minscore = -100
        for threat in threats:
            localthreat = hypothetical_board(local,move)
            score = team*score_board(localthreat) # sign fixed so higher is better
            if minscore == -100 or score < minscore:
                minscore = score
        minscores.append(minscore)
    best = max(minscores)    
    print("best options:")
    for score,move in zip(minscores,moves):
        if score == best:
            print(score,": ", print_move(move))
    candidates = [m for i,m in enumerate(moves) if minscores[i] == best]
    if candidates:
        move = random.choice(candidates)
    else:
        print("still random")
        move = random.choice(moves)
            


    #return (move[1:3][::-1],move[3:5][::-1]),False
    return (move[1:3],move[3:5]),False

def score_board(board,team=None,depth=0):
    if depth > 1:
        return None
    total = 0
    for row in board:
        for elem in row:
            sign = (int(elem>0)-.5)*2
            total += sign * pieceValue[abs(elem)]
    
    #threats = list(possible_moves(board,-team))
    #for threat in threats:
    #    local = hypothetical_board(board,threat)

    return total

def hypothetical_board(board,move):
    move = (move[1:3],move[3:5],False)
    local_board = board.copy()
    movePiece(local_board,*move)
    return local_board


pieceValue = {P : 1,
       fP : 1,
       B : 3,
       N : 3,
       R : 5,
       Q : 9,
       empty : 0,
       K : 100}
