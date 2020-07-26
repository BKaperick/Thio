
# chess.py
## is_valid_move(start, end, team, verbose=0)
>     INPUT
>     start -- array shaped (8,8) containing a board state
>     end -- array shaped (8,8) containing a board state 
>     team -- specifier for team, either `Wh` or `Bl`
>     RETURN
>     * Boolean deciding if exactly one valid chess move by `team` can map `start` 
>     to `end`

## is_promotion(start, end, team, moves, verbose=0)
>     INPUT
>     start -- array shaped (8,8) containing a board state
>     end -- array shaped (8,8) containing a board state 
>     team -- specifier for team, either `Wh` or `Bl`
>     moves -- dictionary encoding details about changes between `start` and `end`
>     RETURN
>     * Boolean determining if the difference between `start` and `end` is in part
>     caused by a promotion
>     NOTE
>     * this only comments on the existence of a promotion by `team`.  This 
>     function does not determine whether other moves are also taking place.
>     However, this check is already performed in `is_valid_move` prior to
>     entering this function

## is_castling(start, end, team, moves, verbose=0)
>     INPUT
>     start -- array shaped (8,8) containing a board state
>     end -- array shaped (8,8) containing a board state 
>     team -- specifier for team, either `Wh` or `Bl`
>     moves -- dictionary encoding details about changes between `start` and `end`
>     Checks whether `team` is castling legally.  Does not make any claims about 
>     whether other moves are also taking place.
>     RETURN
>     * Boolean determining if the difference between `start` and `end` 
>     `team`
>     TODO
>     * Verify indexing is correct.

## is_enpassant(start, end, team, moves, verbose=0)
>     INPUT
>     start -- 2d array storing board state before move
>     end -- 2d array storing board state after move
>     team -- +/- 1 indicating on which team this piece is
>     moves -- dictionary from `is_valid_move` indicating the types of move(s) 
>         made between `start` and `end`
>     verbose -- nonnegative integer indicating level of verbosity for debugging
>     RETURN 
>     move_happened -- a boolean determining whether en passant has taken place
>         by `team`
>     NOTE
>     * this function does not check whether other moves have occurred also

## is_in_check(board, team, verbose=0)
>     Given the board state, determines whether team's king is threatened.

## possible_moves(board, team, pieceloc = None)
>     INPUT
>     board -- array shaped (8,8) containing a board state
>     team -- specifier for team, either `Wh` or `Bl`
>     pieceloc -- if left `None` then all possible moves from all pieces on 
>         `board` on the specified `team` are computed.  Else, only `pieceloc`'s 
>         moves are computed
>     RETURN
>     moves -- a set of 5-tuples of the form (piece-identifier-at-end-of-move, 
>         end-row, end-col) denoting the spaces `pieceloc` piece/team can reach
>     NOTE 
>     * this function does not remove moves which reveal checks illegally,
>     or moves that fail to respond to an active check threat.

## castling_moves(board, team)
>     Returns 5-tuples flagged 'castle' in the first position for each possible
>     castling move in this board state by this team. 
>     Note: This function does not check whether the castling violates check.

## enpassant_moves(board, team, verbose=0)
>     INPUT
>     board -- 2d array storing board state
>     team -- +/- 1 indicating on which team this piece is
>     RETURN 
>     * 5-tuples flagged 'pass left' or 'pass right' in the first position
>     for each possible en'passant move in this board state by this team

## move_to_string(piece, row, col,justloc=0)
## on_board(board, row, col)
>     INPUT
>     board -- 2d array storing board state
>     row -- a rank (row) on [1,8]
>     col -- a file (column) on [1,8]
>     RETURN
>     The piece on `board` at the specified row and column, or `None` if the 
>     coordinates are invalid.

## piece_locations_for_team(board,team)
## moves_on_board(move_tuple)
>     INPUT
>     move_tuple -- an array of 5-tuples containing a piece code, a row, and a column.
>     RETURN
>     * Set of tuples with row and column indices within 1,...,8 range.

## pawn_move(board, row, col, team)
>     INPUT
>     board -- 2d array storing board state
>     row -- index of row at which moves start
>     col -- index of column at which moves start
>     team -- +/- 1 indicating on which team this piece is
>     RETURN
>     moves -- in the form (piece_at_end, end_row, end_col).
>         piece_at_end can be different in the case of promotion.

## knight_move(board, row, col, team)
>     INPUT
>     board -- 2d array storing board state
>     row -- index of row at which moves start
>     col -- index of column at which moves start
>     team -- +/- 1 indicating on which team this piece is
>     RETURN
>     moves -- in the form (N, end_row, end_col) of possible ending squares

## king_move(board, row, col, team)
>     INPUT
>     board -- 2d array storing board state
>     row -- index of row at which moves start
>     col -- index of column at which moves start
>     team -- +/- 1 indicating on which team this piece is
>     RETURN
>     moves -- in the form (K, end_row, end_col) of possible ending squares
>     NOTE
>     * this does not include castling nor does it check for check violations.

## generate_straight(board, start_row, start_col, direction)
>     INPUT
>     board -- 2d array storing board state
>     start_row -- index of row at which moves start
>     start_col -- index of column at which moves start
>     direction -- 2-tuple (+/- 1, +/- 1) indicating the direction of generation
>     YIELD
>     * 3-tuple of the piece, row, and col of next space in sequence

## normal_move(board, row, col, team, sign_pairs)
>     INPUT
>     board -- 2d array storing board state
>     row -- index of row at which moves start
>     col -- index of column at which moves start
>     team -- +/- 1 indicating on which team this piece is
>     sign_pairs -- list of 2-tuples indicating the types of moves allowed.  E.g. 
>         for a rook, this would be [ [-1,0], [1,0], [0,-1], [0,1] ] since it 
>             cannot move diagonally
>     Bishops, Rooks and Queens all move very similarly, so we use the same 
>     function for each of their moves.  sign_pairs is set to allow either 
>     straight moves, diagonal moves, or both.
>     RETURN
>     moves -- set of three tuples of the form [piece, landing_x, landing_y]


# retrograde.py
## piece_count(board, team)
>     {board: [], start: (piece, row, col), end: (piece, row, col)}
>     ('enpassant', row, col)
>     ('OO', kingrow, kingcol)
>     ('OOO', kingrow, kingcol)

## retrograde(board, team, nmoves = 1)
>     INPUT
>     board -- the board object at the current move
>     team -- team which made the most recent move to arrive at board
>     nmoves -- the number of moves to backtrack.
>     RETURN
>     rmoves -- a list of 3-tuples (initial-board, start-coord, end-coord) by 
>         `team` to reach `board`.
>     TODO 
>     * Moves of type (2) as detailed below
>     * Moves of type (3) as detailed below
>     * Extend this to accept nmoves > 1 and build a helper function to do a 
>     single backstep.
>     (1) Find moves into empty squares
>     (2) See how many pieces are missing from opposite team and repeat (1) with taken pieces
>     (3) Special moves like castling/enpassant

## backwards_move_to_board(board, start, end)

# game.py
## Game
###     __init__(self, cpTeam, movemaker)
>         INPUT
>         result -- a string '1' or '0' or '1/2' indicating the game result
>         moves -- a list of moves alternating between white and black moves each 
>         given as a string of standard chess notation.
>         RETURN
>         self -- Game instance
>         Also builds the board to the initial setup ready for simulation.
>         self.board[i,j] is the ith rank (row) and jth file (column), each
>         indexed from 0-7

###     getNextMove(self,before,after,team)
###     getNextUserMove(self,before,after,team)
###     getNextComputerMove(self,team)
###     runGame(self, savestates=True, verbose=0)
>         INPUT
>         savestates -- if is True, the board is deep-copied after each board change.
>         verbose -- if is True, the board is printed after each black move.
>         Iterates over the moves pulled from PGN file and plays the game described, 
>         printing along the way.
>         RETURN
>         states -- if savestates is True, an array of board states detailing the 
>             history of the game, else None

###     createCleanBoard(self)
###     makeMove(self, prevTurnStart, prevTurnEnd, team)
###     checkStraights(self, end, team, piece=R)
>         Given an end coordinate (row,col) on range [1,8] and a team/piece, returns a list 
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
>         prev_move_start - 
>         prev_move_end - 
>         Returns a 2-tuple of the moving pieces

###     movePiece(self, start, end, team, enpassant = False)
>         Given a start and end coordinates (2-lists) and a team 
>         distinction, the board gets updated accordingly.

## on_board_wraparound(board, c1, c2)
>     INPUT
>     row,col
>     Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
>     the specified board position.  Negative indices are treated such that 
>     -1 maps to 8, -2 maps to 7, etc.  This functionality is only used when
>     handling castling and promotions symmetrically.
>     c1==0 and c2==0 are due to checkStraights() or checkDiags() testing a 
>     position which is out of bounds, so None is returned.
>     c1 is a file
>     c2 is a rank

## print_board(board,perspective = Bl)
    Print board in a human-readable format.
## translateMoveToChessNotation(move)
## setCoord(board, c1, c2, val)
>     INPUT is in (row,col) format
>     Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
>     the specified board position and updates self.board with val at this 
>     position.  Negative indices are treated such that -1 maps to 8, -2 maps
>     to 7, etc.  This functionality is only used when
>     handling castling and promotions symmetrically.
>     c1==0 and c2==0 are due to checkStraights() or checkDiags() testing a 
>     position which is out of bounds, so None is returned.

## print_coord(coord)

# test.py

# read_pgn.py
> TODO: Add more data files and seamless reading of multiple files.  (Ideally all .pgn's in ../data directory).
> TODO: Handle en'passant by making pawns "fresh pawns" for exactly one move after a double move.

## HistoricalGame(Game)
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

###     getNextMove(self,_,__,team)
## diffs(board1, board2)
>     INPUT
>     board1 -- a 2d array board state
>     board2 -- a 2d array board state
>     The differences between the two boards are calculated.
>     Importantly, fresh pawns converting back to normal pawns are not included
>     in the array of differences
>     RETURN
>     final_indices -- an array with two arrays [row indices, col indices]
>         pointing to differences between the two inputted boards

## parsePGN(fname, start_count = 0, max_count = 0, verbose=False)
>     INPUT
>     fname -- string name of PGN file
>     start_count -- first game to read in
>     max_count -- maximum number of games to read in
>     verbose -- boolean to print debugging info
>     RETURN
>     games -- list of game objects read from file

## only_correct_games(fname, start_count = 0, max_count = 0, verbose=False)
>     INPUT
>     fname -- string name of PGN file
>     max_count -- maximum number of games to be read from file
>     verbose -- print debugging info
>     YIELD
>     The next game from the PGN file which can be parsed correctly and 
>     completely by Game.runGame().
>     NOTE
>     * specifically, this function checks that Game.runGame()
>     completes without an index error, so it is possible there is still some
>     amount of incorrectness in the Game code.
>     * the PGN files that I have been using to test this code 
>     occasionally have typos in the game itself, and so failures to parse all
>     games in `fname` may be for that reason.  


# play.py
## random_move(board,team)
## score_board(board,team)
## hypothetical_board(board,move)

# main.py
## gen_pairs(games, start_count = 0)
>     INPUT
>     games -- a list of game states
>     YIELD
>     state -- 


# game_wrapper.py
## iter_2d(arr)
## build_data_with_labels(game)
## vectorize(board)
