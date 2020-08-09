'''
TODO: Add more data files and seamless reading of multiple files.  (Ideally all .pgn's in ../data directory).
TODO: Handle en'passant by making pawns "fresh pawns" for exactly one move after a double move.
'''

import numpy as np
from game import *

fname = '../data/Adams.pgn'
    

class HistoricalGame(Game): 
    def __init__(self, result, moves, verbosity=0, save_file = None):
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
        
        BaseGame.__init__(self, verbosity, True, None, save_file)
        
        #Adds null move if white was the last to play
        if len(moves) % 2 == 1:
            moves.append(None)

        #Removes move number from each pair of moves
        self._moves = [(moves[i].split('.')[1],moves[i+1]) for i in range(0, len(moves), 2)]

        if result:
            self.result = result.split('-')[0]
        else:
            self.result = ''

        self._cpTeam = 1

   
    def getNextMove(self,team):
        notation = self._moves[self.movenum-1]
        if team == Wh and notation[0]:
            return self.parseMove(notation[0],team)
        elif team == Bl and notation[1]:
            return self.parseMove(notation[1],team)
        return None




def parsePGN(fname, start_count = 0, max_count = 0, verbose=0):
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
                if verbose: print(moves)            
                if game_count >= start_count:
                    #Create game object from moves
                    games.append(HistoricalGame(moves[-1], moves[:-1], verbose))
                
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
            print("failed on game ", i)
            pass
    

#def clean_file(fname, indices):
#    '''
#    Reads fname and 
#    '''
#    new_fname = fname[:-4] + "_corrected_.pgn"
#    with open(fname) as f:
#        with open(new_fname, "w") as new_f:
            
def gen_pairs(games, start_count = 0):
    '''
    INPUT
    games -- a list of game states

    YIELD
    state -- 
    '''
    for gi, game in enumerate(games):
        game.runGame()
        states = game.states
        team = 1
        for i,state in enumerate(states[:-1]):
            yield state, states[i+1], team, i

            # Alternate team between moves
            team *= -1

def run_history(fname, verbosity):
    games = only_correct_games(fname, start_count = 0, max_count=1, verbose=verbosity)
    
    correct = 0
    total = 0
    
    for start, end, team, index in gen_pairs(games):
        if verbosity:
            print_board(start,team)
            print_board(end,team)
        result = is_valid_move(start, end, team, verbose=verbosity)
        if not result:
            print_board(start)
            print_board(end)
            print(team)
            break
        correct += int(result)
        total += 1
    if verbosity:print("finished: ", correct , " / " , total)
    return correct / total

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
