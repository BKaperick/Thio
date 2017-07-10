from read_pgn import *
from chess import *

def gen_pairs(arr):
    team = 1
    for i in range(len(arr)-1):
        yield arr[i], arr[i+1], team
        team *= -1

if __name__ == "__main__":
    games = parsePGN(fname)
    states = games[0].runGame()
    correct = 0
    total = 0
    for start, end, team in gen_pairs(states):
        result = is_valid_move(start, end, team)
        correct += int(result), total += 1

    print(correct + " / " + total)
    

    
