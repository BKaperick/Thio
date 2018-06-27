from read_pgn import *

Wh = 1
Bl = -1

backrank = {Wh:0, Bl:7}
teams = {n:'White' for n in range(9)}
teams.update({n:'Black' for n in range(-10,0)})
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

def is_valid_move(start, end, team, verbose=0):
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

    diff = diffs(start,end)
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
    #for col, row, bef_piece, aft_piece in zip(*np.where(diff), start[diff], end[diff]):
    for col,row in zip(*diff):
        bef_piece = on_board(start,row,col)
        aft_piece = on_board(end,row,col)
        #if bef_piece == team*fP and aft_piece == team*P:
        #    continue

        # Piece moves to an empty cell
        if bef_piece == empty:
            moves['moveto'].add((abs(aft_piece),row,col))

            # If the moving piece is NOT on the team which should be moving
            # There is absolutely no case where this should occur, so the  
            # function returns `False` immediately
            if aft_piece * team < 0:
                if verbose: print("wrong team(1)")
                return False
        
        # Piece moved away from this space
        elif aft_piece == empty:
            moves['movefrom'].add((abs(bef_piece),row,col))
            
        # This remaining case is where both `bef_piece` and `aft_piece` are 
        # non-empty.  This would occur in 
        # (1) a capture: `bef_piece` is an enemy piece captured by `aft_piece`
        else:
            moves['take'].add((abs(aft_piece),row,col))
            
            # There is no case a square should change and the opposing team
            # ends up on it, so the function returns `False` immediately
            if aft_piece * team < 0: 
                if verbose:
                    print("wrong team(2)")
                    print(aft_piece, bef_piece, team)
                return False
    if verbose:
        print("movefrom: ", [move_to_string(*m,0) for m in moves["movefrom"]])
        print("moveto: ", [move_to_string(*m,0) for m in moves["moveto"]])
        print("take: ", [move_to_string(*m,0) for m in moves["take"]])
    
    # Test to verify that team appropriately responded to a checking threat.
    not_violating_check = not is_in_check(end, team, verbose)
    if not not_violating_check:
        if verbose: print("violating check")
        return False

    enpassant = is_enpassant(start, end, team, moves, verbose)
    # Verifies no other moves took place
    only_enpassant = enpassant and len(diff[0]) == 3

    if enpassant:
        if only_enpassant:
            return True
        if verbose: print("en passant and another move")
        return False

    castling = is_castling(start, end, team, moves, verbose=verbose)
    # Verifies no other moves took place
    only_castling = castling and len(diff[0]) == 4
    
    if castling:
        if only_castling:
            return True
        if verbose: print("castling and another move")
        return False

    # Test to verify exactly one move took place 
    # Specifically, verifies only one previously-occupied space is now empty, 
    # OR it is a castling or en'passant.
    only_one_move = (
        (len(moves['movefrom']) == 1 and
        len(moves['moveto']) + len(moves['take']) == 1))
    
    if not only_one_move:
        if verbose: print("not only_one_move")
        return False
    
    # A test to determine if `start` is converted to `end` through a pawn 
    # promotion
    promotion = is_promotion(start, end, team, moves)
    if promotion:
        return True

    # Iterate over every space which a piece vacates in this move
    for p,x,y in moves['movefrom']:
        start_spc = (x,y)
        # Identify piece which vacates
        piece = on_board(start, x, y)
        # Set of 3-tuples describing all possible moves from start_spc
        end_spaces = possible_moves(start, team, pieceloc = start_spc)
        end_spaces = {tup if tup[0] != 8 else (1,tup[1],tup[2]) for tup in end_spaces}
        # Set of 3-tuples 
        tmp = moves['moveto'].union(moves['take'])
        tmp = {tup if tup[0] != 8 else (1,tup[1],tup[2]) for tup in tmp}
        found_matches = tmp.intersection(end_spaces)
        
        if verbose:
            print("tmp: ", [move_to_string(*m,0) for m in tmp])
            print("possible: ",[move_to_string(*m,0) for m in end_spaces])
            print(move_to_string(p,x,y) + " can move to " + ", ".join([move_to_string(*z,1) for z in found_matches]))
            
        if len(found_matches) == 0:
            return False


    return True

def is_promotion(start, end, team, moves, verbose=0):
    '''
    INPUT
    start -- array shaped (64,) containing a board state
    end -- array shaped (64,) containing a board state 
    team -- specifier for team, either `Wh` or `Bl`
    moves -- dictionary encoding details about changes between `start` and `end`

    RETURN
    * Boolean determining if the difference between `start` and `end` is in part
    caused by a promotion

    NOTE
    * this only comments on the existence of a promotion by `team`.  This 
    function does not determine whether other moves are also taking place.
    However, this check is already performed in `is_valid_move` prior to
    entering this function

    '''
    if verbose > 1:
        print("is_promotion:")
        print(cand_pwn)
        print(cand_pwn[1] == backrank[-team] - team)
        print(on_board(start,cand_pwn[1],cand_pwn[2]) == team * P)
        if len(moves['take']) > 0:
            print(next(iter(moves['take'])))
            print(abs(cand_pwn[2] - cand_prom[2]) == 1)
        else:
            print(next(iter(moves['moveto'])))
            print(not cand_pwn[2] != cand_prom[2])
    # List of potential spaces a pawn could have left for promotion.  
    # These satisfy:
    # (1) This space was vacated this move
    # (2) The space is one rank away from the opposing team's back rank
    # (3) The piece ending at this space is a pawn on `team` 
    cand_pwn = next(iter(moves['movefrom']))
    if not (cand_pwn[1] == backrank[-team] - team and
            on_board(start,cand_pwn[1],cand_pwn[2]) == team * P):
        return False
    # The promoted piece must satisfy:
    # (0) One the correct column
    # (1) Some action took place at this space during this move
    # (2) The space is on the opposing team's back rank
    # (3) The piece ending at this space is not a king
    if len(moves['moveto']) == 1:
        cand_prom = next(iter(moves['moveto']))
        if cand_pwn[2] != cand_prom[2]:
            return False
    else:
        cand_prom = next(iter(moves['take']))
        if abs(cand_pwn[2] - cand_prom[2]) != 1:
            return False
    return cand_prom[1] == backrank[-team] and cand_prom[0] != K


def is_castling(start, end, team, moves, verbose=0):
    '''
    INPUT
    start -- array shaped (64,) containing a board state
    end -- array shaped (64,) containing a board state 
    team -- specifier for team, either `Wh` or `Bl`
    moves -- dictionary encoding details about changes between `start` and `end`

    Checks whether `team` is castling legally.  Does not make any claims about 
    whether other moves are also taking place.

    RETURN
    * Boolean determining if the difference between `start` and `end` 
    `team`

    TODO
    * Verify indexing is correct.
    '''
    
    # Important squares for kingside and queenside castling respectively
    castling_files = ( {'kf':4,'rf':0,'kt':2,'rt':3}, 
                       {'kf':4,'rf':7,'kt':6,'rt':5} )
    
    castling = [False, False]
    for i,files in enumerate(castling_files):
        
        if verbose > 1:
            print("is in check: ", is_in_check(start, team))
            print((K,backrank[team],files['kf']) in moves['movefrom'])
            print((R,backrank[team],files['rf']) in moves['movefrom'])
            print((K,backrank[team],files['kt']) in moves['moveto'])
            print((R,backrank[team],files['rt']) in moves['moveto'])
            print(on_board(start,backrank[team],files['rf']) == team*R)
            print(on_board(start,backrank[team],files['kf']) == team*K)
            print(on_board(end,backrank[team],files['kt']) == team*K)
            print(on_board(end,backrank[team],files['rt']) == team*R)

        # This boolean verifies the team is not in check and the king and rook 
        # are in the correct places before and after the move
        castling[i] = bool(not is_in_check(start, team) and
        (K,backrank[team],files['kf']) in moves['movefrom'] and
        (R,backrank[team],files['rf']) in moves['movefrom'] and
        (K,backrank[team],files['kt']) in moves['moveto'] and
        (R,backrank[team],files['rt']) in moves['moveto'] and
        on_board(start,backrank[team],files['rf']) == team*R and
        on_board(start,backrank[team],files['kf']) == team*K and
        on_board(end,backrank[team],files['kt']) == team*K and
        on_board(end,backrank[team],files['rt']) == team*R)

    if verbose: print("castling: ", castling)    
    return sum(castling) == 1

def is_enpassant(start, end, team, moves, verbose=0):
    '''
    INPUT
    start -- 2d array storing board state before move
    end -- 2d array storing board state after move
    team -- +/- 1 indicating on which team this piece is
    moves -- dictionary from `is_valid_move` indicating the types of move(s) 
        made between `start` and `end`
    verbose -- nonnegative integer indicating level of verbosity for debugging

    RETURN 
    move_happened -- a boolean determining whether en passant has taken place
        by `team`

    NOTE
    * this function does not check whether other moves have occurred also
    '''
    passes = enpassant_moves(start, team)
    if verbose > 1:
        print("is_enpassant")
        print(moves)
        print(passes)
    
    # Verifies en'passant happened
    move_happened = False
    for passant in passes:
        if passant[0] == 'pass left':
            direction = 1#team
        elif passant[0] == 'pass right':
            direction = -1#team
        if verbose > 1:
            print((P,passant[1],passant[2]) in moves['moveto'])
            print((fP,passant[1]-team, passant[2]) in moves['movefrom'])
            print(team,direction)
            print((P,passant[1]-team, passant[2]+direction) in moves['movefrom'])
        
        move_happened = (not move_happened and
        (P,passant[1],passant[2]) in moves['moveto'] and
        (fP,passant[1]-team, passant[2]) in moves['movefrom'] and
        (P,passant[1]-team, passant[2]+direction) in moves['movefrom'])
    if verbose>1:
        print("en passant returning ", move_happened)
    return move_happened

def is_in_check(board, team, verbose=0):
    '''
    Given the board state, determines whether team's king is threatened.
    '''
    # List of all moves the opponent can make.
    threats = possible_moves(board, -team)
    if verbose > 1:
        print([move_to_string(*th) for th in threats])

    for flag,x,y in threats:
        if on_board(board, x, y) == K:
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
        end-row, end-col) denoting the spaces `pieceloc` piece/team can reach

    NOTE 
    * this function does not remove moves which reveal checks illegally,
    or moves that fail to respond to an active check threat.
    '''
    if pieceloc:
        piece_locs = {pieceloc}
    else:
        piece_locs = zip(*np.where(board*team > 0))
    moves = set()
    for x,y in piece_locs:
        if on_board(board, x, y) == team*P or on_board(board, x, y) == team*fP: 
            moves ^= pawn_move(board, x, y, team)
        elif on_board(board, x, y) == team*N: 
            moves ^= knight_move(board, x, y, team)
        elif on_board(board, x, y) == team*Q:
            moves ^= normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1), (1,0), (0,1), (-1,0), (0,-1)])
        elif on_board(board, x, y) == team*B:
            moves ^= normal_move(board, x, y, team, [(-1,-1), (-1,1), (1,-1), (1,1)])
        elif on_board(board, x, y) == team*R:
            moves ^= normal_move(board, x, y, team, [(0,-1), (0,1), (-1,0), (1,0)])
        elif on_board(board, x, y) == team*K:
            moves ^= king_move(board, x, y, team)
    
    #moves += castling_moves(board, team)
    #moves += enpassant_moves(board, team)
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
        if on_board(board, br, files['kf']) == team*K and on_board(board, br, files['rf']) == team*R:

            # Verify spaces between rook and king are empty.
            for f in range(min(files['rf'],files['kf'])+1, max(files['rf'],files['kf'])):
                if on_board(board, br, f) != empty:
                    moves[ind] = False
                    break
    return [m for m in moves if m]

def enpassant_moves(board, team):
    '''
    INPUT
    board -- 2d array storing board state
    team -- +/- 1 indicating on which team this piece is

    RETURN 
    * 3-tuples flagged 'pass left' or 'pass right' in the first position
    for each possible en'passant move in this board state by this team
    '''
    moves = []

    # The only rank on which enemy fresh pawns can be located.
    fourth_rank = backrank[-team] - 3*team
    
    # Files on which these fresh pawns are found
    enemy_freshpawn_locs = [i for i,x in enumerate(board[:, fourth_rank]) if x == -team*fP]
    
    for y in enemy_freshpawn_locs:

        # If one of team's pawns is in the position to en'passant a fresh pawn,
        # add it to list.
        if on_board(board, fourth_rank, y+1) == team*P:
            moves.append(('pass left', fourth_rank+team, y))
        if on_board(board, fourth_rank, y-1) == team*P:
            moves.append(('pass right', fourth_rank+team, y))
            #import pdb; pdb.set_trace()
    return moves


def move_to_string(piece, row, col,justloc=0):
    if justloc:
        out = ""
    else:
        if piece == None:
            piece = "None"
        else:
            #piece = teams[piece] + " " + piece_to_string[abs(piece)]
            piece = piece_to_string[abs(piece)]
        out = "A " + piece + " at "
    return out + chr(col + 97) + str(row+1)


def on_board(board, row, col):
    '''
    INPUT
    board -- 2d array storing board state
    row -- a file (column) on [0,7]
    col -- a rank (row) on [0,7]

    RETURN
    The piece on `board` at the specified row and column, or `None` if the 
    coordinates are invalid.
    '''
    if 0 <= row <= 7 and 0 <= col <= 7:
        return board[col, row]
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
    INPUT
    board -- 2d array storing board state
    row -- index of row at which moves start
    col -- index of column at which moves start
    team -- +/- 1 indicating on which team this piece is

    RETURN
    moves -- in the form (piece_at_end, end_row, end_col).
        piece_at_end can be different in the case of promotion.
    '''

    moves = set()
    if on_board(board, row+team, col) == empty:
        moves = {(P, row+team, col)}
        
        # Handle double-move if have not moved previously.
        if on_board(board, row+2*team,col) == empty and row == backrank[team] + team:
            moves.add((P,row+2*team, col))
    
    # Attacks
    candidates = {(row+team,col+1), (row+team,col-1)}
    for cand in candidates:
        pieceval = on_board(board, cand[0], cand[1])
        if pieceval and pieceval* team < 0:
            # attacking promotion
            if row == backrank[-team] - team:
                for p_code in piece.values():
                    if p_code != K:
                        moves.add((p_code, cand[0], cand[1]))
            else:
                moves.add((P, cand[0], cand[1]))
            

    # Handle promotions
    if row == backrank[-team] - team:
        if on_board(board, backrank[-team], col) == empty:
            for p_code in piece.values():
                if p_code != K:
                    moves.add((p_code, row+team, col))
    return moves_on_board(moves)

def knight_move(board, row, col, team):
    '''
    INPUT
    board -- 2d array storing board state
    row -- index of row at which moves start
    col -- index of column at which moves start
    team -- +/- 1 indicating on which team this piece is

    RETURN
    moves -- in the form (N, end_row, end_col) of possible ending squares
    '''

    moves = set()
    for x in [-2,-1,1,2]:
        for y in [-2,-1,1,2]:
            if abs(x) == abs(y): continue
            pieceval = on_board(board, row+x, col+y)
            if pieceval != None and pieceval*team <= 0:
                moves.add((N,row+x,col+y))
    return moves_on_board(moves)

def king_move(board, row, col, team):
    '''
    INPUT
    board -- 2d array storing board state
    row -- index of row at which moves start
    col -- index of column at which moves start
    team -- +/- 1 indicating on which team this piece is

    RETURN
    moves -- in the form (K, end_row, end_col) of possible ending squares
    
    NOTE
    * this does not include castling nor does it check for check violations.
    '''

    moves = set()
    for x in [-1,0,1]:
        for y in [-1,0,1]:
            if x==0 and y==0: continue
            pieceval = on_board(board, row+x, col+y)
            if pieceval != None and pieceval*team <= 0:
                moves.add((K,row+x,col+y))
    return moves_on_board(moves)

def generate_straight(board, start_row, start_col, direction):
    '''
    INPUT
    board -- 2d array storing board state
    start_row -- index of row at which moves start
    start_col -- index of column at which moves start
    direction -- 2-tuple (+/- 1, +/- 1) indicating the direction of generation

    YIELD
    * 3-tuple of the piece, row, and col of next space in sequence
    '''
    for mult in range(1,8):
        new_x = start_row + direction[0]*mult
        new_y = start_col + direction[1]*mult
        if 0 <= new_x <= 7 and 0 <= new_y <= 7:
            yield on_board(board, new_x, new_y), new_x, new_y

def normal_move(board, row, col, team, sign_pairs):
    '''
    INPUT
    board -- 2d array storing board state
    row -- index of row at which moves start
    col -- index of column at which moves start
    team -- +/- 1 indicating on which team this piece is
    sign_pairs -- list of 2-tuples indicating the types of moves allowed.  E.g. 
        for a rook, this would be [ [-1,0], [1,0], [0,-1], [0,1] ] since it 
            cannot move diagonally

    Bishops, Rooks and Queens all move very similarly, so we use the same 
    function for each of their moves.  sign_pairs is set to allow either 
    straight moves, diagonal moves, or both.
    
    RETURN
    moves -- set of three tuples of the form [piece, landing_x, landing_y]
    '''
    moves = set()
    this_piece = abs(on_board(board, row, col))
    for direction in sign_pairs:
        for piece,x,y in generate_straight(board, row, col, direction):
            # Note that `generate_straight` already checks for boundary violations
            if piece == empty:
                moves.add((this_piece, x, y))
            else:
                if piece*team < 0:
                    moves.add((this_piece, x, y))
                break
    return moves
