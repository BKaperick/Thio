
./chess.py----------------------------------------------------------------------
is_valid_move(start, end, team)
    Takes in two arrays shaped (64,) and determines if exactly one valid chess 
    move by the specified team can map start to end.
    TODO: Decide whether (64,) or (8,8) shape is preferable.  Consider 
    efficiency of reshape().
    TODO: Finish implementing subfunctions.

is_castling(start, end, team, moves)
    Checks whether team is castling legally.  Does not make any claims about 
    whether other moves are also taking place.
    TODO: Verify indexing is correct.

is_enpassant(start, end, team, moves)
    Determines whether start can be transformed into end by an en'passant move
    by team.
    TODO: Implement.

is_in_check(board, team)
    Given the board state, determines whether team's king is threatened.
    TODO: Implement.


./game_wrapper.py---------------------------------------------------------------
iter_2d(arr)
build_data_with_labels(game)
vectorize(board)

./read_pgn.py-------------------------------------------------------------------
TODO: Add more data files and seamless reading of multiple files.  (Ideally all .pgn's in ../data directory).

Game
    __init__(self, result, moves)
        result - is a string '1' or '0' or '1/2' indicating the game result
        moves - a list of moves alternating between white and black moves given
        in standard chess notation.

        Also builds the board to the initial setup ready for simulation.
        self.board[i,j] is the ith rank (row) and jth file (column), each
        indexed from 0-7

    runGame(self, savestates=True, verbose=False)
        Iterates over the moves pulled from PGN file and plays the game described, 
        printing along the way.

        If savestates is True, the board is deep-copied after each board change.
        If verbose is True, the board is printed after each black move.

    checkStraights(self, end, team, piece=R)
        Given an end coordinate on range [1,8] and a team/piece, returns a list 
        of all pieces of this team and this piece type which could have reached 
        end with a straight movement.

    checkDiags(self, end, team, piece=B)
        Given an end coordinate and a team/piece, returns a list of all pieces
        of this team and this piece type which could have reached end with a 
        diagonal movement.

    ambiguous(self, starts, move)
        starts is a list returned from checkStraights() or checkDiags() 
        which contains a list of coordinates of pieces which could make 
        the inputted move.

    clarifyMove(self, move, team)
        move - string containing standard chess notation for the move
        team - corresponds to one of the two team codes

        Returns a 2-tuple of the moving pieces

    coord(self, c1, c2)
        Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
        the specified board position.  Negative indices are treated such that 
        -1 maps to 8, -2 maps to 7, etc.  This functionality is only used when
        handling castling and promotions symmetrically.
        
        c1==0 and c2==0 are due to checkStraights() or checkDiags() testing a 
        position which is out of bounds, so None is returned.

    setCoord(self, c1, c2, val)
        Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
        the specified board position and updates self.board with val at this 
        position.  Negative indices are treated such that -1 maps to 8, -2 maps
        to 7, etc.  This functionality is only used when
        handling castling and promotions symmetrically.
        
        c1==0 and c2==0 are due to checkStraights() or checkDiags() testing a 
        position which is out of bounds, so None is returned.

    movePiece(self, start, end, team)
        Given a start and end string in standard chess notation and a team 
        distinction, the board gets updated accordingly.

    Print(self)
        Print board in a human-readable format.
parsePGN(fname)
    Take in a string file location fname and return a list of games.
    Games list is comprised of Game objects.

