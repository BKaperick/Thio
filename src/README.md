
# ./chess.py
## is_valid_move(start, end, team, verbose=False)
>     INPUT
>     start -- array shaped (64,) containing a board state
>     end -- array shaped (64,) containing a board state 
>     team -- specifier for team, either `Wh` or `Bl`
>     RETURN
>     * Boolean deciding if exactly one valid chess move by `team` can map `start` 
>     to `end`
>     TODO
>     * Decide whether (64,) or (8,8) shape is preferable.  Consider efficiency 
>     of reshape().  This is probably not a very important issue.

## is_promotion(start, end, team, moves, verbose=False)
>     INPUT
>     start -- array shaped (64,) containing a board state
>     end -- array shaped (64,) containing a board state 
>     team -- specifier for team, either `Wh` or `Bl`
>     moves -- dictionary encoding details about changes between `start` and `end`
>     RETURN
>     * Boolean determining if the difference between `start` and `end` is in part
>     caused by a promotion
>     Note, this only comments on the existence of a promotion by `team`.  This 
>     function does not determine whether other moves are also taking place.

## is_castling(start, end, team, moves, verbose=False)
>     INPUT
>     start -- array shaped (64,) containing a board state
>     end -- array shaped (64,) containing a board state 
>     team -- specifier for team, either `Wh` or `Bl`
>     moves -- dictionary encoding details about changes between `start` and `end`
>     RETURN
>     * Boolean determining if the difference between `start` and `end` 
>     `team`
>     Checks whether team is castling legally.  Does not make any claims about 
>     whether other moves are also taking place.
>     TODO
>     * Verify indexing is correct.

## is_enpassant(start, end, team, moves)
>     Determines whether start can be transformed into end by exactly one 
>     en'passant move by the specified team.

## is_in_check(board, team)
>     Given the board state, determines whether team's king is threatened.

## possible_moves(board, team, pieceloc = None)
>     Given a board state and a team specifier, returns a list of 3-tuples
>     describing the possible (end positions of?) moves that can be made.
>     Note: this function does not remove moves which reveal checks illegally,
>     or moves that fail to respond to an active check threat.

## castling_moves(board, team)
>     Returns 3-tuples flagged 'castle' in the first position for each possible
>     castling move in this board state by this team. 
>     Note: This function does not check whether the castling violates check.

## enpassant_moves(board, team)
>     Returns 3-tuples flagged 'pass left' or 'pass right' in the first position
>     for each possible en'passant move in this board state by this team. 
>     Note: This function does not check whether the castling violates check.

## on_board(board, x,y)
>     x is a file (column) on [0,7]
>     y is a rank (row) on [0,7]

## moves_on_board(move_tuple)
>     INPUT
>     move_tuple -- an array of 3-tuples containing a piece code, a row, and a column.
>     RETURN
>     * Set of tuples with row and column indices within 0,...,7 range.

## pawn_move(board, row, col, team)
>     Returns moves in the form (piece_at_and, end_row, end_col).
>     piece_at_end can be different in the case of promotion.

## knight_move(board, row, col, team)
## king_move(board, row, col, team)
>     Note, this does not include castling nor does it check for check violations.

## generate_straight(board, start_row, start_col, direction)
>     Generator for the successive row,column and piece along a straight line
>     indicated by the direction 2-tuple.

## normal_move(board, row, col, team, sign_pairs)
>     INPUT
>     board -- 2d array storing board state
>     row -- index of row at which moves start
>     col -- index of column at which moves start
>     team -- +/- 1 indicating on which team this piece is
>     sign_pairs -- list of 2-tuples indicating the types of moves allowed.  E.g. 
>     for a rook, this would be [ [-1,0], [1,0], [0,-1], [0,1] ] since it cannot 
>     move diagonally
>     Bishops, Rooks and Queens all move very similarly, so we use the same function
>     for each of their moves.  sign_pairs is set to allow either 
>     straight moves, diagonal moves, or both.
>     RETURN
>     moves -- set of three tuples of the form [piece, landing_x, landing_y]

## retrograde(board, team, nmoves = 1)
>     INPUT
>     board -- the board object at the current move
>     team -- team which made the most recent move to arrive at board
>     nmoves -- the number of moves to backtrack.
>     RETURN
>     rmoves -- a list of 2-tuples of moves by `team` to reach `board`.
>     TODO 
>     * Moves of type (2) as detailed below
>     * Moves of type (3) as detailed below
>     * Extend this to accept nmoves > 1 and build a helper function to do a 
>     single backstep.
>     (1) Find moves into empty squares
>     (2) See how many pieces are missing from opposite team and repeat (1) with taken pieces
>     (3) Special moves like castling/enpassant


# ./read_pgn.py
> TODO: Add more data files and seamless reading of multiple files.  (Ideally all .pgn's in ../data directory).
> TODO: Handle en'passant by making pawns "fresh pawns" for exactly one move after a double move.

## Game
###     __init__(self, result, moves)
>         INPUT
>         result -- a string '1' or '0' or '1/2' indicating the game result
>         moves -- a list of moves alternating between white and black moves each 
>         given as a string of standard chess notation.
>         RETURN
>         self -- Game instance
>         Also builds the board to the initial setup ready for simulation.
>         self.board[i,j] is the ith rank (row) and jth file (column), each
>         indexed from 0-7

###     runGame(self, savestates=True, verbose=0)
>         Iterates over the moves pulled from PGN file and plays the game described, 
>         printing along the way.
>         If savestates is True, the board is deep-copied after each board change.
>         If verbose is True, the board is printed after each black move.

###     checkStraights(self, end, team, piece=R)
>         Given an end coordinate on range [1,8] and a team/piece, returns a list 
>         of all pieces of this team and this piece type which could have reached 
>         end with a straight movement.

###     checkDiags(self, end, team, piece=B)
>         Given an end coordinate and a team/piece, returns a list of all pieces
>         of this team and this piece type which could have reached end with a 
>         diagonal movement.

###     ambiguous(self, starts, move)
>         starts is a list returned from checkStraights() or checkDiags() 
>         which contains a list of coordinates of pieces which could make 
>         the inputted move.

###     clarifyMove(self, move, team, prev_move_start, prev_move_end)
>         move - string containing standard chess notation for the move
>         team - corresponds to one of the two team codes
>         Returns a 2-tuple of the moving pieces

###     coord(self, c1, c2)
>         Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
>         the specified board position.  Negative indices are treated such that 
>         -1 maps to 8, -2 maps to 7, etc.  This functionality is only used when
>         handling castling and promotions symmetrically.
>         c1==0 and c2==0 are due to checkStraights() or checkDiags() testing a 
>         position which is out of bounds, so None is returned.
>         c1 is a file
>         c2 is a rank

###     setCoord(self, c1, c2, val)
>         Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
>         the specified board position and updates self.board with val at this 
>         position.  Negative indices are treated such that -1 maps to 8, -2 maps
>         to 7, etc.  This functionality is only used when
>         handling castling and promotions symmetrically.
>         c1==0 and c2==0 are due to checkStraights() or checkDiags() testing a 
>         position which is out of bounds, so None is returned.

###     movePiece(self, start, end, team, enpassant = False)
>         Given a start and end coordinates (2-lists) and a team 
>         distinction, the board gets updated accordingly.

## diffs(board1, board2)
## print_board(board)
    Print board in a human-readable format.
## parsePGN(fname, max_count = 0, verbose=False)
>     INPUT
>     fname -- string name of PGN file
>     max_count -- maximum number of games to read in
>     verbose -- boolean to print debugging info
>     RETURN
>     games -- list of game objects read from file

## only_correct_games(fname, max_count = 0, verbose=False)
>     INPUT
>     fname -- string name of PGN file
>     max_count -- maximum number of games to be read from file
>     verbose -- print debugging info
>     YIELD
>     The next game from the PGN file which can be parsed correctly and 
>     completely by Game.runGame().
>     Specifically, this function checks that Game.runGame()
>     completes without an index error, so it is possible there is still some
>     amount of incorrectness in the Game code.
>     Note that the PGN files that I have been using to test this code 
>     occasionally have typos in the game itself, and so failures to parse all
>     games in `fname` may be for that reason.  


# ./main.py
## gen_pairs(games)
>     INPUT
>     games -- a list of game states
>     YIELD
>     state -- 


# ./game_wrapper.py
## iter_2d(arr)
## build_data_with_labels(game)
## vectorize(board)
