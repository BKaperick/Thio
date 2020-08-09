# Thio
## Project Overview
The (eventual) scope of this project is *analyzing* games in a very particular way.  The problem of interest is that of *Retrograde Analysis*.  In general, this is the challenge of recreating previous game states from a mid-game state.  

Given the board state at turn `n`, we seek to recreate the game state after `n-1`, `n-2`, ..., 1, 0` turns.  We will use openly-accessible professional games to aid in the training of an algorithm for this task.

## Getting Started
Currently supported options to get started:

### Playing
In addition to the retrograde analysis, Thio is a fully-capable chess-playing program.  It uses a rudimentary alpha-beta pruned minimax implementation, with a naive analysis of the game state.  Soon, we'll add a small database to store some opening lines to make his openings more natural.

Most variations of standard chess notation will suffice as input, e.g. 'e4' is interpreted as 'Make the only possible pawn move which ends on e3'.  For any ambiguities, as is standard, specify a command such as 'Nce4' to mean 'Move the knight on the c file to e4'.

An input of one character, such as 'x' or 'q' will save (if a save_file is specified) and exit the game.  To load an existing game, specify a `load_file`.  By default, `save_file` is set to `load_file` and the game state after each turn is appended to the file.  See `src/game.py` for the human-friendly file format for saving and loading.
```
$python main.py play [White/Black] [load_file] [save_file]
```

### Retrograde Analysis
The command to read the PGN files into memory is `$python main.py hist [verbosity]`.  The retrograde analysis is still not fully developed, but see `src/retrograde.py` for the current status.

## Development Notes
The command to execute all unit tests is simply `$python main.py test [verbosity]`.

Some quirks of the code which are useful for development and use of this repo.

* Chess boards are encoded as size (8,8) numpy arrays of 8-bit signed integers.  Each empty space is denoted by `0` and each unique piece type has an integer value.  The black pieces are negative, and white pieces positive.  These values are defined in `read_pgn.py` as capital letters at the start of the file.
    * The recommended way to access a piece at a particular board position is to call `on_board(board, row, col)` which accepts `row` and `col` as positive integers in the range 1,...,8.  It automatically performs an out of bounds check for safety.
    * Be careful, as pawns have a different integer value on the move immediately after making a 2-space forward advancement.  This is to allow the proper encoding of En Passant moves, which can only be made on the move immediately after such a double move has been performed by the opponent.  **A common mistake is to perform a check like** `on_board(board, row, col) == P` **which will fail to find a recently-double-advanced pawn**.

* Moves are typically encoded as a 5-tuple of `(piece-code-at-end-of-move, row-at-start-of-move, col-at-start-of-move, row-at-end-of-move, col-at-end-of-move)`.  For example Bc1-d2 becomes `(B, 1, 3, 1, 4)`, and a pawn promotion on e1 would be `(Q, 2, 4, 1, 4)`.  
