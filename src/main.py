from read_pgn import *
from chess import *
from itertools import chain

def gen_pairs(games):
    '''
    INPUT
    games -- a list of game states

    YIELD
    state -- 
    '''
    for gi, game in enumerate(games):
        print("game number: ", gi)
        states = game.runGame(verbose=0)
        team = 1
        for i,state in enumerate(states[:-1]):
            yield state, states[i+1], team, i

            # Alternate team between moves
            team *= -1

if __name__ == "__main__":
    games = only_correct_games(fname, verbose=0)
    
    #states = []
    #for game in games:
    #    states += game.runGame()

    #chain([games[ind].runGame() for ind in game_indices])

    correct = 0
    total = 0
    
    for start, end, team, index in gen_pairs(games):
        print(index)
        result = is_valid_move(start, end, team, verbose=0)
        if not result:
            print("failed: ", index)
            print_board(start)
            print_board(end)
            print(team)
            break
        correct += int(result)
        total += 1

    print("finished: ", correct , " / " , total)
    

    
