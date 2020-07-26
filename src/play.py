from chess import *
import random

def random_move(board,team):
    moves = list(possible_moves(board,team))
    print("options:",moves)
    return random.choice(moves)

# Create new human-vs-computer game with the computer as black, using `random_move` to make its moves
game = Game(Bl, random_move)

game.runGame()
