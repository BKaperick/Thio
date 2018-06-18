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

def is_valid_move(start, end, team, verbose=False):
    '''
    INPUT
    start -- array shaped (64,) containing a board state
    end -- array shaped (64,) containing a board state 
    team -- specifier for team, either `Wh` or `Bl`

    RETURN
    * Boolean deciding if exactly one valid chess move by `team` can map `start` 
    to `end`

    TODO
    * Decide whether (64,) or (8,8) shape is preferable.  Consider efficiency 
    of reshape().  This is probably not a very important issue.
    '''

    diff = start != end
    moves = {
            'moveto':set(),
            'movefrom':set(),
            'take':set(),
            }
    
    # This loop builds the `moves` dictionary.
    # Iterate over all spaces which are different between the start and end board
    # row -- the row that was changed (a file in range [0,...,7])
    # col -- the col that was changed (a rank in range [0,...,7])
    # bef_piece -- specifier for the piece at this position on `start`
    # aft_piece -- specifier for the piece at this position on `end`
    for row, col, bef_piece, aft_piece in zip(*np.where(diff), start[diff], end[diff]):
        
        # `fP` is a temporary distinction for a pawn which has just performed 
        # en'passant, so this difference is just a pawn reverting to its correct
        # ID, not a real move.
        if bef_piece == team*fP and aft_piece == team*P:
            continue

        # Piece moves to an empty cell
        if bef_piece == empty:
            moves['moveto'].add((row,col))

            # If the moving piece is NOT on the team which should be moving
            # There is absolutely no case where this should occur, so the  
            # function returns `False` immediately
            if aft_piece * team < 0:
                if verbose: print("wrong team(1)")
                return False
        
        # Piece moved away from this space
        elif aft_piece == empty:
            moves['movefrom'].add((row,col))
            
        # This remaining case is where both `bef_piece` and `aft_piece` are 
        # non-empty.  This would occur in 
        # (1) a capture: `bef_piece` is an enemy piece captured by `aft_piece`
        else:
            moves['take'].add((row,col))
            
            # There is no case a square should change and the opposing team
            # ends up on it, so the function returns `False` immediately
            if aft_piece * team < 0: 
                if verbose:
                    print("wrong team(2)")
                    print(aft_piece, bef_piece, team)
                return False

    enpassant = is_enpassant(start, end, team, moves)

    # A test to determine if `start` is converted to `end` through a pawn 
    # promotion
    # TODO: incorporate this check in the more stringent verification which has
    # not yet been implemented.  (See the TODO later on in this function)
    promotion = is_promotion(start, end, team, moves)

    # A basic test to verify the number of pieces moved away from squares is equal
    # to the number which moved to squares (or this move is an en'passant where 
    # 2 pieces are removed but only 1 is added back)
    moves_add_up = len(moves['moveto']) + len(moves['take']) == len(moves['movefrom']) or enpassant

    # Test to verify exactly one move took place 
    # Specifically, verifies only one previously-occupied space is now empty, 
    # OR it is a castling or en'passant.
    only_one_move = len(moves['movefrom']) == 1 or is_castling(start, end, team, moves) or enpassant

    # TODO
    # very important to verify each simple move does not change the type of piece
    # For example, a bishop could move to a knight and this would not raise 
    # issue in this function
    # 

    # Iterate over every space which a piece vacates in this move
    for start_spc in moves['movefrom']:
        # Identify piece which vacates
        piece = start[start_spc]
        # Set of 3-tuples describing all possible moves from start_spc
        end_spaces = possible_moves(start, team, pieceloc = start_spc)
        # Set of 3-tuples 
        found_matches = (moves['moveto'].union(moves['take'])).intersection(end_spaces)
        print('mv_t:',moves['moveto'])
        print('es:',end_spaces)
        print('fm:',found_matches)
        if len(found_matches) == 0:
            return False


    # Test to verify that team appropriately responded to a checking threat.
    not_violating_check = not is_in_check(end, team)

    if verbose:
        print("moves_add_up", moves_add_up)
        print("only_one_move", only_one_move)
        print("violating_check", not not_violating_check)
        print("is castling", is_castling(start, end, team, moves))
        print("en passant", enpassant)
        print("\n")

    return moves_add_up and only_one_move and not_violating_check


def is_promotion(start, end, team, moves, verbose=False):
    '''
    INPUT
    start -- array shaped (64,) containing a board state
    end -- array shaped (64,) containing a board state 
    team -- specifier for team, either `Wh` or `Bl`
    moves -- dictionary encoding details about changes between `start` and `end`

    RETURN
    * Boolean determining if the difference between `start` and `end` is in part
    caused by a promotion

    Note, this only comments on the existence of a promotion by `team`.  This 
    function does not determine whether other moves are also taking place.
    '''
    
    # List of potential spaces a pawn could have left for promotion.  
    # These satisfy:
    # (1) This space was vacated this move
    # (2) The space is one rank away from the opposing team's back rank
    # (3) The piece ending at this space is a pawn on `team` 
    candidate_pawns = [piece[1] for piece in moves['movefrom'] 
            if piece[0] == backrank[-team] - team and start[piece] == team * P]
    
    if len(candidate_pawns) == 0:
        return False
    
    # List of potential spaces a pawn could have promoted at.  These satisfy:
    # (1) Some action took place at this space during this move
    # (2) The space is on the opposing team's back rank
    # (3) The piece ending at this space is not a king
    # 
    # Note we do not need to verify this piece is on the correct team, since 
    # that check is already performed in the construction of `moves`
    candidate_promoted = [piece[1] for piece in moves['moveto'] 
            if piece[0] == backrank[-team] and piece * team != team * K]
    
    # Simply verify there is at least one element in each list with the same 
    # column
    for pwn in candidate_pawns:
        for prm in candidate_promoted:
            if pwn[1] == prm[1]:
                return True

    return False


def is_castling(start, end, team, moves, verbose=False):
    '''
    INPUT
    start -- array shaped (64,) containing a board state
    end -- array shaped (64,) containing a board state 
    team -- specifier for team, either `Wh` or `Bl`
    moves -- dictionary encoding details about changes between `start` and `end`

    RETURN
    * Boolean determining if the difference between `start` and `end` 
    `team`

    Checks whether team is castling legally.  Does not make any claims about 
    whether other moves are also taking place.

    TODO
    * Verify indexing is correct.
    '''

    # Important squares for kingside and queenside castling respectively
    castling_files = ( {'kf':4,'rf':0,'kt':2,'rt':3}, 
                       {'kf':4,'rf':7,'kt':6,'rt':5} )

    # See TODO in `is_valid_move`
    start = start.reshape((8,8))
    end = end.reshape((8,8))
    
    castling = [False, False]
    for i,files in enumerate(castling_files):
        
        if verbose:
            print("is in check: ", is_in_check(start, team))
            print((files['kf'],backrank[team]) in moves['movefrom'])
            print((files['rf'],backrank[team]) in moves['movefrom'])
            print((files['kt'],backrank[team]) in moves['moveto'])
            print((files['rt'],backrank[team]) in moves['moveto'])
            print(start[files['rf'],backrank[team]] == team*R)
            print(start[files['kf'],backrank[team]] == team*K)
            print(end[files['kt'],  backrank[team]] == team*K)
            print(end[files['rt'],  backrank[team]] == team*R)

        # This boolean verifies the team is not in check and the king and rook 
        # are in the correct places before and after the move
        castling[i] = bool(not is_in_check(start, team) and
        (files['kf'],backrank[team]) in moves['movefrom'] and
        (files['rf'],backrank[team]) in moves['movefrom'] and
        (files['kt'],backrank[team]) in moves['moveto'] and
        (files['rt'],backrank[team]) in moves['moveto'] and
        start[files['rf'],backrank[team]] == team*R and
        start[files['kf'],backrank[team]] == team*K and
        end[files['kt'],  backrank[team]] == team*K and
        end[files['rt'],  backrank[team]] == team*R)

    if verbose: print("castling: ", castling)    
    return sum(castling) == 1

def is_enpassant(start, end, team, moves):
    '''
    Determines whether start can be transformed into end by exactly one 
    en'passant move by the specified team.
    '''
    start = start.reshape((8,8))
    end = end.reshape((8,8))
    passes = enpassant_moves(start, team)
    
    # Verifies no other moves took place
    #diff = np.where(start != end)
    diff = diffs(start, end)
    if len(diff[0]) > 3:
        return False
    

    # Verifies en'passant happened
    move_happened = False
    for passant in passes:
        if passant[0] == 'pass left':
            direction = team
        elif passant[0] == 'pass right':
            direction = -team
        move_happened = not move_happened and ...
        (passant[1],passant[2]) in moves['moveto'] and ...
        (passant[1], passant[2]-team) in moves['movefrom'] and ...
        (passant[1]+direction, passant[2]-team) in moves['movefrom']
    
    return move_happened

def is_in_check(board, team):
    '''
    Given the board state, determines whether team's king is threatened.
    '''
    # List of all moves the opponent can make.
    threats = possible_moves(board, -team)

    for flag,x,y in threats:
        if board[x,y] == team*K:
            return True
    return False

def possible_moves(board, team, pieceloc = None): 
    '''
    INPUT
    board -- array shaped (64,) containing a board state
    team -- specifier for team, either `Wh` or `Bl`
    pieceloc -- if left `None` then all possible moves from all pieces on 
        `board` on the specified `team` are computed.  Else, only `pieceloc`'s 
        moves are computed

    RETURN
    moves -- a set of 3-tuples of the form (piece-identifier-at-end-of-move, 
        end-row, end-col)

    NOTE 
    * this function does not remove moves which reveal checks illegally,
    or moves that fail to respond to an active check threat.
    '''
    if pieceloc:
        opposing_piece_locs = {pieceloc}
    else:
        opposing_piece_locs = zip(*np.where(board*team < 0))
    print('opl:',opposing_piece_locs)
    moves = set()
    for x,y in opposing_piece_locs:
        if board[x,y] == team*P: 
            moves ^= pawn_move(board, x, y, team)
        elif board[x,y] == team*N: 
            moves ^= knight_move(board, x, y, team)
        elif board[x,y] == team*Q:
            moves ^= normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1), (1,0), (0,1), (-1,0), (0,-1)])
        elif board[x,y] == team*B:
            moves ^= normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1)])
        elif board[x,y] == team*R:
            moves ^= normal_move(board, x, y, team, [(0,-1), (0,1), (-1,0), (1,0)])
    
    #moves += castling_moves(board, team)
    #moves += enpassant_moves(board, team)
    return moves


#def possible_moves(board, team): 
#    '''
#    Given a board state and a team specifier, returns a list of 3-tuples
#    describing the possible (end positions of?) moves that can be made.
#    
#    Note: this function does not remove moves which reveal checks illegally,
#    or moves that fail to respond to an active check threat.
#    '''
#    opposing_piece_locs = zip(*np.where(board*team < 0))
#    moves = []
#    for x,y in opposing_piece_locs:
#        if board[x,y] == team*P: 
#            moves += pawn_move(board, x, y, team)
#        elif board[x,y] == team*N: 
#            moves += knight_move(board, x, y, team)
#        elif board[x,y] == team*Q:
#            moves += normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1), (1,0), (0,1), (-1,0), (0,-1)])
#        elif board[x,y] == team*B:
#            moves += normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1)])
#        elif board[x,y] == team*R:
#            moves += normal_move(board, x, y, team, [(0,-1), (0,1), (-1,0), (1,0)])
#    
#    #moves += castling_moves(board, team)
#    #moves += enpassant_moves(board, team)
#    return moves

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
                    moves[ind] = False
                    break
    return [m for m in moves if m]

def enpassant_moves(board, team):
    '''
    Returns 3-tuples flagged 'pass left' or 'pass right' in the first position
    for each possible en'passant move in this board state by this team. 

    Note: This function does not check whether the castling violates check.
    '''
    moves = []

    # The only rank on which enemy fresh pawns can be located.
    fourth_rank = backrank[-team] - 3*team
    
    # Files on which these fresh pawns are found
    enemy_freshpawn_locs = [i for i,x in enumerate(board[:,fourth_rank]) if x == -team*fP]
    
    for y in enemy_freshpawn_locs:

        # If one of team's pawns is in the position to en'passant a fresh pawn,
        # add it to list.
        if on_board(board, y+1, fourth_rank) == team*P:
            moves.append(('pass left', y, fourth_rank+team))
        if on_board(board, y-1, fourth_rank) == team*P:
            moves.append(('pass right', y, fourth_rank+team))
    return moves
            

def on_board(board, x,y):
    '''
    x is a file (column) on [0,7]
    y is a rank (row) on [0,7]
    '''
    if 0 <= x <= 7 and 0 <= y <= 7:
        return board[x,y]
    return None

def moves_on_board(move_tuple):
    '''
    INPUT
    move_tuple -- an array of 3-tuples containing a piece code, a row, and a column.
    
    RETURN
    * Set of tuples with row and column indices within 0,...,7 range.
    '''
    return set([(p,r,c) for p,r,c in move_tuple if 0 <= r <= 7 and 0 <= c <= 7])


def pawn_move(board, row, col, team):
    '''
    Returns moves in the form (piece_at_and, end_row, end_col).
    piece_at_end can be different in the case of promotion.
    '''
    moves = set()
    if board[row+team,col] == empty:
        moves = {(P, row+team, col)}
        
        # Handle double-move if have not moved previously.
        if board[row+2*team,col] == empty and row == backrank[team] + team:
            moves.add((row+2*team, col))
    
    # Attacks
    candidates = {(row+team,col+1), (row+team,col-1)}
    for cand in candidates:
        moves.add((P, row+team,col+1))
        moves.add((P, row+team,col-1))

    # Handle promotions
    if row == backrank[-team] - team:
        for p_code in piece.values():
            if p_code != K:
                moves.add((p_code, row+team, col))
    print('pm: ',moves)
    return moves_on_board(moves)

def knight_move(board, row, col, team):
    moves = set()
    for x in [-2,-1,1,2]:
        for y in [-2,-1,1,2]:
            if abs(x) == abs(y): continue
            if board[row+x,col+y]*team <= 0:
                moves.add((N,row+x,col+y))
    return moves_on_board(moves)

def king_move(board, row, col, team):
    '''
    Note, this does not include castling nor does it check for check violations.
    '''
    moves = set()
    for x in [-1,0,1]:
        for y in [-1,0,1]:
            if x==0 and y==0: continue
            if board[row+x,col+y]*team <= 0:
                moves.add((K,row+x,col+y))
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
    INPUT
    board -- 2d array storing board state
    row -- index of row at which moves start
    col -- index of column at which moves start
    team -- +/- 1 indicating on which team this piece is
    sign_pairs -- list of 2-tuples indicating the types of moves allowed.  E.g. 
    for a rook, this would be [ [-1,0], [1,0], [0,-1], [0,1] ] since it cannot 
    move diagonally

    Bishops, Rooks and Queens all move very similarly, so we use the same function
    for each of their moves.  sign_pairs is set to allow either 
    straight moves, diagonal moves, or both.
    
    RETURN
    moves -- set of three tuples of the form [piece, landing_x, landing_y]
    '''
    moves = set()
    this_piece = board[row, col]
    for direction in sign_pairs:
        for piece,x,y in generate_straight(board, row, col, direction):
            if piece == empty:
                moves.add((this_piece, x, y))
            else:
                if piece*team < 0:
                    moves.add((this_piece, x, y))
                break
    # Note, we don't need to use moves_on_board() since generate_straight
    # already checks for boundary violations.
    return moves

def retrograde(board, team, nmoves = 1):
    '''
    INPUT
    board -- the board object at the current move
    team -- team which made the most recent move to arrive at board
    nmoves -- the number of moves to backtrack.

    RETURN
    rmoves -- a list of 2-tuples of moves by `team` to reach `board`.

    TODO 
    * Moves of type (2) as detailed below
    * Moves of type (3) as detailed below
    * Extend this to accept nmoves > 1 and build a helper function to do a 
    single backstep.
    
    (1) Find moves into empty squares
    (2) See how many pieces are missing from opposite team and repeat (1) with taken pieces
    (3) Special moves like castling/enpassant
    '''

    # List containing location of every piece on `team`
    piece_locs = zip(*np.where(board*team > 0))
    rmoves = []
    for x,y in piece_locs:
        if board[x,y] == team*N: 
            rmoves += knight_move(board, x, y, team)
        elif board[x,y] == team*Q:
            rmoves += normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1), (1,0), (0,1), (-1,0), (0,-1)])
        elif board[x,y] == team*B:
            rmoves += normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1)])
        elif board[x,y] == team*R:
            rmoves += normal_move(board, x, y, team, [(0,-1), (0,1), (-1,0), (1,0)])

    possible_moves = []
    
    return moves
