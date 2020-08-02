from chess import *
from game import *
import random

eps = .001
MAXDEPTH = 4
def alphabeta(board,maxdepth,team):
    return _alphabeta(board,maxdepth,-1000,1000,team,team)

def _alphabeta(board,depth,alpha,beta,cpTeam,team,verbose=0):
    indent = "    "*(MAXDEPTH - depth)
    if depth == 0:
        score = cpTeam*score_board(board)
        if verbose>0:print(indent,"scoring: ",team, score)
        return None, score
    moves = list(real_possible_moves(board,team,depth))
    random.shuffle(moves)
    if team == cpTeam:
        value = -1000
        best_move = None
        for move in moves:
            child_board = hypothetical_board(board,move)
            if verbose>0:print(indent,"move: ", print_move(move))
            _,newval = _alphabeta(child_board,depth-1,alpha, beta, cpTeam,-team)
            if newval > value:
                if value > -1000:
                    if verbose>0:print(indent,"(",alpha,"): choosing ",print_move(move)," (",newval,") over ",print_move(best_move)," (",value,")")
                best_move = move
                value = newval
            alpha = max(alpha, value)
            if alpha > beta:
                #print("alpha={0} > beta={1}",alpha,beta)
                break
        return best_move,value
    value = 1000
    best_move = None
    for move in moves:
        child_board = hypothetical_board(board,move)
        
        # best move for opponent (lowest score)
        if verbose>0:print(indent,"response: ",print_move(move))
        _,newval = _alphabeta(child_board, depth-1, alpha, beta, cpTeam,-team)
        if newval < value:
            if value < 1000:
                if verbose>0:print(indent,"(",beta,"): ",print_move(move)," (",newval,") is a stronger response than ",print_move(best_move)," (",value,")")
            best_move = move
            value = newval

        beta = min(beta, value)
        if beta <= alpha:
            #print("alpha={0} >= beta={1}",alpha,beta)
            break
    if team != cpTeam:
        if verbose>0:print(indent,"White would play ",print_move(best_move)," since it attains his best score ",value)
    return best_move,value
        
def alphabeta_move(board,team,movenum):
    minscores = []
    move,score = alphabeta(board,MAXDEPTH,team)
    return (move[1:3],move[3:5]),False

def alphabeta_adj_move(board,team,movenum):
    depth = 3
    minscores = []
    score = score_board(board)

    if team*score < -5:
        depth += 1
    if movenum < 8:
        depth -= 1
    
    move,score = alphabeta(board,depth,team)
    return (move[1:3],move[3:5]),False
    

def real_possible_moves(board,team,depth):
    moves = list(possible_moves(board,team))
    real_moves = []
    for move in moves:
        child_board = hypothetical_board(board,move)
        if not is_in_check(child_board,team):
            real_moves.append(move)
        else:
            if depth == MAXDEPTH:
                print("CAN'T PLAY ",print_move(move), " SINCE IT VIOLATES CHECK")
    return real_moves

def iterate_board(board):
    for _c,col in enumerate(board):
        for _r,row in enumerate(col):
            r = _r+1
            c = _c+1
            yield on_board(board,r,c),r,c

def score_board(board):
    total = 0
    foundWhiteKing = False
    foundBlackKing = False
    for piece,row,col in iterate_board(board):
        if piece == Wh*K:
            foundWhiteKing = True
        elif piece == Bl*K:
            foundBlackKing = True
        sign,piece_value = signed_value(piece)
        if 2 < row and row < 7 and 2 < col and col < 7:
            piece_value *= 1.1
        total += piece_value
    if not foundWhiteKing:
        total -= 1000
    if not foundBlackKing:
        total += 1000

    if on_board(board,1,5) != K:
        total -= .1
    if on_board(board,8,5) != -K:
        total += .1
    return total

def hypothetical_board(board,move):
    move = (move[1:3],move[3:5],False)
    local_board = board.copy()
    movePiece(local_board,*move)
    return local_board

def signed_value(piece):
    sign = (int(piece>0)-.5)*2
    return sign,sign * pieceValue[abs(piece)]
pieceValue = {P : 1,
       fP : 1,
       B : 3,
       N : 3,
       R : 5,
       Q : 9,
       empty : 0,
       K : 600}
