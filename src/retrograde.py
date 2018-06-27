from chess import *

def retrograde(board, team, nmoves = 1):
    '''
    INPUT
    board -- the board object at the current move
    team -- team which made the most recent move to arrive at board
    nmoves -- the number of moves to backtrack.

    RETURN
    rmoves -- a list of 3-tuples (initial-board, start-coord, end-coord) by 
        `team` to reach `board`.

    TODO 
    * Moves of type (2) as detailed below
    * Moves of type (3) as detailed below
    * Extend this to accept nmoves > 1 and build a helper function to do a 
    single backstep.
    
    (1) Find moves into empty squares
    (2) See how many pieces are missing from opposite team and repeat (1) with taken pieces
    (3) Special moves like castling/enpassant
    '''
    
    # TODO
    # * create set() of all pieces which have been removed from -`team`'s side
    enemy_piece_locs = zip(*np.where(board*team < 0))
    expected_piece_count = {
            P: 8,
            R: 2,
            N: 2,
            B: 2,
            K: 1,
            Q: 1,
            empty: 1
    }
    
    

    #enemy_pieces_missing = {K,Q,B,N,R,P,fP}
    for row, col in enemy_piece_locs:
        enemy_piece = on_board(board, row, col)
        piece_val = abs(enemy_piece) if abs(enemy_piece) != fP else P
        expected_piece_count[piece_val] -= 1
    
    piece_types_left = {k for k,v in expected_piece_count if v > 0}

    # List containing location of every piece on `team`
    piece_locs = zip(*np.where(board*team > 0))

    rmoves = []
    for row, col in piece_locs:
        if on_board(board, row, col) == team*N: 
            rmoves += knight_move(board, row, col, team)
        elif on_board(board, row, col) == team*Q:
            rmoves += normal_move(board, row, col, team, 
                    [(-1,-1), (-1,1), (1,-1), (1,1), (1,0), (0,1), (-1,0), 
                        (0,-1)])
        elif on_board(board, row, col) == team*B:
            rmoves += normal_move(board, row, col, team, 
                    [(-1,-1), (-1,1), (1,-1), (1,1)])
        elif on_board(board, row, col) == team*R:
            rmoves += normal_move(board, row, col, team, 
                    [(0,-1), (0,1), (-1,0), (1,0)])
    
    possible_moves = []
    
    return moves
