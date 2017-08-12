from read_pgn import *
from chess import *
from itertools import chain

def gen_pairs(games):
    '''
    games is a list of game states
    '''
    for game in games:
        states = game.runGame()
        team = 1
        for i in range(len(states)-1):
            yield states[i], states[i+1], team
            team *= -1

if __name__ == "__main__":
    games = parsePGN(fname, 4)
    games = only_correct_games(fname, games)
    
    #states = []
    #for game in games:
    #    states += game.runGame()

    #chain([games[ind].runGame() for ind in game_indices])

    correct = 0
    total = 0
    
    for start, end, team in gen_pairs(games):
        result = is_valid_move(start, end, team, verbose=0)
        if not result:
            print("failed: ")
            print_board(start)
            print_board(end)
            print(team)
            break
        correct += int(result)
        total += 1

    print("finished: ", correct , " / " , total)
    

    
