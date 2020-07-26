'''
TODO: Add more data files and seamless reading of multiple files.  (Ideally all .pgn's in ../data directory).
TODO: Handle en'passant by making pawns "fresh pawns" for exactly one move after a double move.
'''

import numpy as np
from game import *

fname = '../data/Adams.pgn'
piece_to_string = {
        fP: '(f)Pawn',
        P: 'Pawn',
        R: 'Rook',
        N: 'Knight',
        B: 'Bishop',
        Q: 'Queen',
        K: 'King',
        C: '<Castling>',
        empty: 'Empty'}
    

class HistoricalGame(Game): 
    def __init__(self, result, moves):
        '''
        INPUT
        result -- a string '1' or '0' or '1/2' indicating the game result
        moves -- a list of moves alternating between white and black moves each 
        given as a string of standard chess notation.

        RETURN
        self -- Game instance

        Also builds the board to the initial setup ready for simulation.
        self.board[i,j] is the ith rank (row) and jth file (column), each
        indexed from 0-7
        '''
        
        #Adds null move if white was the last to play
        if len(moves) % 2 == 1:
            moves.append(None)

        #Removes move number from each pair of moves
        self._moves = [(moves[i].split('.')[1],moves[i+1]) for i in range(0, len(moves)-5, 2)]

        if result:
            self.result = result.split('-')[0]
        else:
            self.result = ''

        #Initializes board to chess starting position
        self.createCleanBoard()

        self.movenum = 0
   
    def getNextMove(self,team):
        move = self._moves[self.movenum]
        if team == Wh:
            return move[0]
        else:
            return move[1]



def diffs(board1, board2):
    '''
    INPUT
    board1 -- a 2d array board state
    board2 -- a 2d array board state

    The differences between the two boards are calculated.
    Importantly, fresh pawns converting back to normal pawns are not included
    in the array of differences

    RETURN
    final_indices -- an array with two arrays [row indices, col indices]
        pointing to differences between the two inputted boards
    '''
    diff = board1 != board2
    indices = np.where(diff)
    final_indices = [[], []]
    for x,y in zip(*indices):
        # `fP` is a temporary distinction for a pawn which has just performed 
        # a two space jump and can be en'passanted, so this difference is just 
        # a pawn reverting to its correct ID, not a real move.
        if abs(board1[x,y]) == fP and abs(board2[x,y]) == P and board1[x,y]*board2[x,y] > 0:
            continue
        final_indices[0].append(x)
        final_indices[1].append(y)
    return final_indices

def parsePGN(fname, start_count = 0, max_count = 0, verbose=False):
    '''
    INPUT
    fname -- string name of PGN file
    start_count -- first game to read in
    max_count -- maximum number of games to read in
    verbose -- boolean to print debugging info

    RETURN
    games -- list of game objects read from file
    '''
    games = []
    inMoves = False
    moves = ''
    game_count = -1
    with open(fname) as pgn:
        for line in pgn.readlines():
            if verbose: print(line, end='')
            
            #Start of a game
            if line[0] == '1':
                game_count += 1
                inMoves = True
             
            #End of a game
            elif inMoves and line == '\n':
                moves = moves.split()
                
                if game_count >= start_count:
                    #Create game object from moves
                    games.append(HistoricalGame(moves[-1], moves[:-1]))
                
                inMoves = False
                moves = ''
                
                # Read at most max_count games
                if len(games) == start_count + max_count:
                    break
                
            #Middle of a game
            if inMoves:
                moves += line.replace('\n',' ')
            
    
    return games

def only_correct_games(fname, start_count = 0, max_count = 0, verbose=False):
    '''
    INPUT
    fname -- string name of PGN file
    max_count -- maximum number of games to be read from file
    verbose -- print debugging info

    YIELD
    The next game from the PGN file which can be parsed correctly and 
    completely by Game.runGame().
    
    NOTE
    * specifically, this function checks that Game.runGame()
    completes without an index error, so it is possible there is still some
    amount of incorrectness in the Game code.

    * the PGN files that I have been using to test this code 
    occasionally have typos in the game itself, and so failures to parse all
    games in `fname` may be for that reason.  
    '''
    # The error check code calls runGame() which can only be called once per
    # game, so they must be regenerated.
    games = parsePGN(fname, start_count = start_count, max_count=max_count, verbose=verbose)
    fresh_games = parsePGN(fname, start_count = start_count, max_count=max_count, verbose=verbose)
    
    # Identifies games which run without error
    correct_game_indices = []
    for i,g in enumerate(games):
        try:
            g.runGame()
            correct_game_indices.append(i)
            yield fresh_games[i]
        except IndexError:
            pass
    

#def clean_file(fname, indices):
#    '''
#    Reads fname and 
#    '''
#    new_fname = fname[:-4] + "_corrected_.pgn"
#    with open(fname) as f:
#        with open(new_fname, "w") as new_f:
            


if __name__ == "__main__":

    games = only_correct_games(fname, parsePGN(fname))
    #games[14].runGame(False, True)
    tally = 0
    for i,g in enumerate(games):
        if i%100==0: print(i)
        try:
            g.runGame()
            tally += 1
        except IndexError:
            print("failed")
    print(tally / float(len(games)))
