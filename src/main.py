from read_pgn import *
from chess import *
from itertools import chain

def gen_pairs(arr):
    team = 1
    for i in range(len(arr)-1):
        yield arr[i], arr[i+1], team
        team *= -1

if __name__ == "__main__":
    games = parsePGN(fname)
    games = only_correct_games(fname, games)
    
    states = []
    for game in games:
        states += game.runGame()

    #chain([games[ind].runGame() for ind in game_indices])

    correct = 0
    total = 0
    for start, end, team in gen_pairs(states):
        result = is_valid_move(start, end, team)
        correct += int(result)
        total += 1

    print(correct , " / " , total)
    

    
