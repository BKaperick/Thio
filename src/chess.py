from read_pgn import *

Wh = 1
Bl = -1

backrank = {Wh:0, Bl:7}

P = 1
fP = 8
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
            (files['kf'],backrank[team]) in moves['movefrom'] and
            (files['rf'],backrank[team]) in moves['movefrom'] and
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
    '''
    # List of all moves the opponent can make.
    threats = possible_moves(board, -team)

    for _,x,y in threats:
        if board[x,y] == team*K:
            return True
    return False

def possible_moves(board, team): 
    '''
    Given a board state and a team specifier, returns a list of 3-tuples
    describing the possible moves that can be made.
    
    Note: this function does not remove moves which reveal checks illegally,
    or moves that fail to respond to an active check threat.

    TODO: en'passant moves.
    '''
    piece_locs = zip(np.where(board*team < 0))
    moves = []
    for x,y in opposing_piece_locs:
        if board[x,y] == team*P: 
            moves += pawn_move(board, x, y, team)
        elif board[x,y] == team*N: 
            moves += knight_move(board, x, y, team)
        elif board[x,y] == team*Q:
            moves += normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1), (1,0), (0,1), (-1,0), (0,-1)])
        elif board[x,y] == team*B:
            moves += normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1)])
        elif board[x,y] == team*R:
            moves += normal_move(board, x, y, team, [(0,-1), (0,1), (-1,0), (1,0)])
    
    moves += castling_moves(board, team)
    moves += enpassant_moves(board, team)
    return moves

def castling_moves(board, team):
    '''
    Returns 3-tuples flagged 'castle' in the first position for each possible
    castling move in this board state by this team. 

    Note: This function does not check whether the castling violates check.
    '''
    # Important squares for kingside and queenside castling respectively
    castling_files = ( {'kf':4,'rf':0,'kt':2,'rt':3}, 
                       {'kf':4,'rf':7,'kt':6,'rt':5} )
    br = backrank[team]
    moves = [('castle', 2, br), ('castle', 6, br)]
    for ind,files in enumerate(castling_files):
        if board[files['kf'],br] == team*K and board[files['rf'],br] == team*R:

            # Verify spaces between rook and king are empty.
            for f in range(min(files['rf'],files['kf'])+1, max(files['rf'],files['kf'])):
                if board[f, br] != empty:
                    del moves[ind]
                    break
    return moves

def enpassant_moves(board, team):
    '''
    Returns 3-tuples flagged 'pass left' or 'pass right' in the first position
    for each possible en'passant move in this board state by this team. 

    Note: This function does not check whether the castling violates check.
    '''
    moves = []
    fourth_rank = backrank[-team] - 3*team
    enemy_freshpawn_locs = [i for i,x in enumerate(board[fourth_rank,:]) if x == -team*fP]
    for y in enemy_freshpawn_locs:
        if on_board(board, fourth_rank, y+1) == team*P:
            moves.append('pass left', fourth_rank+team, y+1)
        if on_board(board, fourth_rank, y-1) == team*P:
            moves.append('pass right', fourth_rank+team, y+1)
    return moves
            

def on_board(board, x,y):
    if 0 <= x <= 7 and 0 <= y <= 7:
        return board[x,y]
    return None

def move_on_board(move_tuple):
    return [(p,r,c) for p,r,c in move_tuple if 0 <= r <= 7 and 0 <= c <= 7]


def pawn_move(board, row, col, team):
    '''
    Returns moves in the form (piece_at_and, end_row, end_col).
    piece_at_end can be different in the case of promotion.
    '''
    if board[row+team,col] == empty:
        moves = [(P, row+team, col)]
        
        # Handle double-move if have not moved previously.
        if board[row+2*team,col] == empty and row == backrank[team] + team:
            moves.append(row+2*team, col)
    
    # Attacks
    candidates = {(row+team,col+1), (row+team,col-1)}
    for cand in candidates:
        moves.append([P, row+team,col+1])
        moves.append([P, row+team,col-1])

    # Handle promotions
    elif row == backrank[-team] - team:
        for p_code in piece.values():
            if p_code != K:
                moves.append(p_code, row+team, col)

    return moves_on_board(moves)

def knight_move(board, row, col, team):
    moves = []
    for x in [-2,-1,1,2]:
        for y in [-2,-1,1,2]:
            if abs(x) == abs(y): continue
            if board[row+x,col+y]*team <= 0:
                moves.append(N,row+x,col+y)
    return moves_on_board(moves)

def king_move(board, row, col, team):
    '''
    Note, this does not include castling nor does it check for check violations.
    '''
    moves = []
    for x in [-1,0,1]:
        for y in [-1,0,1]:
            if x==0 and y==0: continue
            if board[row+x,col+y]*team <= 0:
                moves.append(K,row+x,col+y)
    return moves_on_board(moves)

def generate_straight(board, start_row, start_col, direction):
    '''
    Generator for the successive row,column and piece along a straight line
    indicated by the direction 2-tuple.
    '''
    for x in range(8):
        for y in range(8):
            new_x = start_row + direction[0]*x
            new_y = start_col + direction[1]*y
            if 0 <= new_x <= 7 and 0 <= new_y <= 7:
                yield board[new_x, new_y], new_x, new_y

def normal_move(board, row, col, team, sign_pairs):
    '''
    Bishops, Rooks and Queens all move very similarly, so we use the same function
    for each of their moves, with only sign_pairs changing to allow either 
    straight moves, diagonal moves, or both.
    '''
    moves = []
    this_piece = board[row, col]
    for direction in sign_pairs:
        for piece,x,y in generate_straight(board, row, col, direction):
            if piece == empty:
                moves.append(this_piece, x, y)
            else:
                if piece*team < 0:
                    moves.append(this_piece, x, y)
                break
    # Note, we don't need to use moves_on_board() since generate_straight
    # already checks for boundary violations.
    return moves

