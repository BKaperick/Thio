# Thio

The scope of this project is being changed from *playing* chess to *analyzing* games in a very particular way.  The problem of interest is that of *Retrograde Analysis*.  In general, this is the challenge of recreating previous game states from a mid-game state.  

Given the board state at turn $n$, this project seeks to recreate the game state after $n-1,\, n-2, \, \dots,\, 1, \, 0$ turns.  To accomplish this, we will experiment with machine learning using openly-accessible pro games.

## Development Notes
Some quirks of the code which are useful for development and use of this repo.

* Chess boards are encoded as size (8,8) numpy arrays of 8-bit signed integers.  Each empty space is denoted by `0` and each unique piece type has an integer value.  The black pieces are negative, and white pieces positive.  These values are defined in `read_pgn.py` as capital letters at the start of the file.
    * Be careful because pawns have a different integer value on the move immediately after making a 2-space forward advancement.  This is to allow the proper encoding of En Passant moves, which can only be made on the move immediately after such a double move has been performed by the opponent.  **A common mistake is to perform a check like** `on_board(board, row, col) == P` **which will fail on a recently-double-advanced pawn**.

* Moves are typically encoded as a 3-tuple of `(piece-code-at-end-of-move, row-at-end-of-move, col-at-end-of-move)`.  For example Bc1-d2 becomes `(B, 1, 4)`, and a pawn promotion on e1 would be `(Q, 0, 4)`.  **A common mistake is to put a negative value in the first position for a black move.  The first position is always positive**.

* Verify everything is working correctly by running `$python main.py` which will run the code through the test data set `Adams.pgn` and ensure game parsing is working.
You can pass in an optional command line argument as a positive integer to indicate the level of verbosity for debugging.  Currently 1 and 2 are implemented to give increasing levels of debugging comments.

* `chess.py` contains all the code to check whether two boards can be related by a single move.  The important function here is `is_valid_move` which answers this question fully.
