Wh = 1
Bl = -1
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
    Takes in two arrays shaped (64,) and determines if a valid chess move
    can map start to end.
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
            if sign(aft_piece 
        
        # Piece moved away from this cell
        elif aft_piece == empty:
            moves['movesfrom'].append(row,col)

        else:
            moves['take'].append(row,col)
    
    # A basic test to verify the number of pieces moved away from squares is equal
    # to the number which moved to squares
    moves_add_up = len(moves['moveto']) + len(moves['take']) != len(moves['movesfrom'])

    # Test to verify exactly one move took place 
    # (Note this fails for castling and en'passant)
    only_one_move = len(moves['movefrom']) == 1 or is_castling(start, end) or is_enpassant(start, end)

    return moves_add_up and only_one_move

def is_castling(start, end):

def is_enpassant(start, end):
    
