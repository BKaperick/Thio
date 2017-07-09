Wh = 1
Bl = -1

backrank = {Wh:0, Bl:7}

P = 1
R = 2
N = 3
B = 4
Q = 5
K = 6
C = 7
O = 7
empty = 0

def is_valid_move(start, end, team):
    '''
    Takes in two arrays shaped (64,) and determines if exactly one valid chess 
    move by the specified team can map start to end.
    TODO: Decide whether (64,) or (8,8) shape is preferable.  Consider 
    efficiency of reshape().
    TODO: Finish implementing subfunctions.
    '''
    diff = start != end
    moves = {
            'moveto':[],
            'movefrom':[],
            'take':[],
            }
    for (row,col), bef_piece, aft_piece in zip(np.where(diff), start[diff], end[diff]):
                
        # Piece moves to an empty cell
        if bef_piece == empty:
            moves['moveto'].append(row,col)

            # If the moving piece is NOT on the team which should be moving
            if aft_piece * team < 0:
                return False
        
        # Piece moved away from this cell
        elif aft_piece == empty:
            moves['movesfrom'].append(row,col)
            
            # If the moving piece is NOT on the team which should be moving
            if bef_piece * team < 0:
                return False


        else:
            moves['take'].append(row,col)
            
            # If one's own piece is taken, or the wrong team acted
            if aft_piece * team < 0 or bef_piece * team > 0:
                return False
    
    # A basic test to verify the number of pieces moved away from squares is equal
    # to the number which moved to squares
    moves_add_up = len(moves['moveto']) + len(moves['take']) != len(moves['movesfrom'])

    # Test to verify exactly one move took place 
    # (Note this fails for castling and en'passant)
    only_one_move = len(moves['movefrom']) == 1 or is_castling(start, end, team, moves) or is_enpassant(start, end, team, moves)

    # Test to verify that team appropriately responded to a checking threat.
    not_violating_check = not is_in_check(end, team)

    return moves_add_up and only_one_move and not_violating_check

def is_castling(start, end, team, moves):
    '''
    Checks whether team is castling legally.  Does not make any claims about 
    whether other moves are also taking place.
    TODO: Verify indexing is correct.
    '''

    # Important squares for kingside and queenside castling respectively
    castling_files = ( {'kf':4,'rf':0,'kt':2,'rt':3}, 
                       {'kf':4,'rf':7,'kt':6,'rt':5} )
    start = start.reshape((8,8))
    end = end.reshape((8,8))
    
    castling = False
    for files in castling_files:

        # This boolean verifies the team is not in check and the king and rook 
        # are in the correct places before and after the move
        castling = not is_in_check(start, team) and
        (files['kf'],backrank[team]) in moves['movefrom'] 
        and (files['rf'],backrank[team]) in moves['movefrom'] and
            (files['kt'],backrank[team]) in moves['movesto'] and 
            (files['rt'],backrank[team]) in moves['movesto'] and
            start[files['rf'],backrank[team]] == team*R and 
            start[files['kf'],backrank[team]] == team*K and 
            end[files['kt'],backrank[team]] == team*K and 
            end[files['kf'],backrank[team]] == team*R
    
    return castling

def is_enpassant(start, end, team, moves):
    '''
    Determines whether start can be transformed into end by an en'passant move
    by team.
    TODO: Implement.
    '''
    return False

def is_in_check(board, team):
    '''
    Given the board state, determines whether team's king is threatened.
    TODO: Implement.
    '''
    opposing_pieces = board[board*team < 0]

