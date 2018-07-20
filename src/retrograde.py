from chess import *

def piece_count(board, team):
    piece_locs = zip(*np.where(board*team > 0))
    expected_piece_count = {
            P: 8,
            R: 2,
            N: 2,
            B: 2,
            K: 1,
            Q: 1,
            empty: 1
    }
    '''
    {board: [], start: (piece, row, col), end: (piece, row, col)}
    ('enpassant', row, col)
    ('OO', kingrow, kingcol)
    ('OOO', kingrow, kingcol)
    '''

    #enemy_pieces_missing = {K,Q,B,N,R,P,fP}
    for row, col in piece_locs:
        enemy_piece = on_board(board, row, col)
        piece_val = abs(piece) if abs(piece) != fP else P
        expected_piece_count[piece_val] -= 1
    
    piece_types_left = {k for k,v in expected_piece_count if v > 0}
    return piece_types_left

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
    
    piece_types_left = piece_count(board, -team)

    # List containing location of every piece on `team` at the end of this move
    piece_locs = zip(*np.where(board*team > 0))

    moves = []
    boards = set()
    for row, col in piece_locs:
        piece = on_board(board, row, col)
        
        # All moves where a Knight takes another piece
        if piece == team*N: 
            # All possible moves from ENDSPACE to STARTSPACE
            # ENDSPACE is the location of an enemy piece at the end of move
            tmp_moves = knight_move(board, row, col, team)
            moves = [(move, (N, row, col)) for move in tmp_moves]

        # All moves where a Queen takes another piece
        elif piece == team*Q:
            tmp_moves = normal_move(board, row, col, team, 
                    [(-1,-1), (-1,1), (1,-1), (1,1), (1,0), (0,1), (-1,0), 
                        (0,-1)])
            moves = [(move, (Q, row, col)) for move in tmp_moves]

        # All moves where a Bishop takes another piece
        elif piece == team*B:
            tmp_moves = normal_move(board, row, col, team, 
                    [(-1,-1), (-1,1), (1,-1), (1,1)])
            moves = [(move, (B, row, col)) for move in tmp_moves]

        # All moves where a Rook takes another piece
        elif piece == team*R:
            tmp_moves = normal_move(board, row, col, team, 
                    [(0,-1), (0,1), (-1,0), (1,0)])
            moves = [(move, (R, row, col)) for move in tmp_moves]
        
        # All moves where a 
        if row == backrank[-team]:
            

    for start, end in moves:
        start_d, start_r, start_c = start
        end_d, end_r, end_c = end
        preboard = board.copy()
        preboard[start_c-1, start_r-1] = empty
        preboard[end_c-1, end_r-1] = team*end_d
        boards.add(preboard)
    
    special_moves = {'OO', 'OOO', 'enpassant', 'promotion'}
    return moves, boards

def backwards_move_to_board(board, start, end):

if __name__ == '__main__':
    verbosity = int(argv[1]) if len(argv) > 1 else 0
    games = only_correct_games(fname, start_count = 0, max_count=1, verbose=verbosity)
    
    correct = 0
    total = 0
    
    for start, end, team, index in gen_pairs(games):
        start in retrograde(end)

    print("finished: ", correct , " / " , total)
    

    
