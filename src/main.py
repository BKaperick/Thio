from read_pgn import *
from chess import *
from play import *
from test import *
from itertools import chain
from sys import argv

'''
COMMAND-LINE options:
py main.py play White
py main.py play Black
py main.py test
py main.py hist [verbosity]
'''

def gen_pairs(games, start_count = 0):
    '''
    INPUT
    games -- a list of game states

    YIELD
    state -- 
    '''
    for gi, game in enumerate(games):
        print("game number: ", gi + start_count)
        game.runGame()
        states = game.states
        team = 1
        for i,state in enumerate(states[:-1]):
            yield state, states[i+1], team, i

            # Alternate team between moves
            team *= -1

if __name__ == "__main__":
    if len(argv) == 1:
        pass
    mode = argv[1]    
    if mode == "play":
        if len(argv) > 3 and argv[3] == "Black":
           team = Wh
        else:
            team = Bl
        # Create new human-vs-computer game with the computer as `team`, using `random_move` to make its moves
        #game = Game(team, random_move)
        game = Game(team, alphabeta_adj_move, verbosity=1)
        game.runGame()
    elif mode == "test":
        verbosity = int(argv[2]) if len(argv) > 2 else 0
        game = TestGame(verbosity)
        game.runAllTests()
    elif mode == "hist":
        verbosity = int(argv[2])
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
        print("finished: ", correct , " / " , total)
        

    
