from read_pgn import Game
import numpy as np

def iter_2d(arr):
    i = 0
    for row in enumerate(arr):
        for cell in enumerate(row):
            yield i,cell
            i += 1

def build_data_with_labels(game):
    states = game.runGame()
    

def vectorize(board):
    vector = board.reshape((64,))

    # Normalize data to avoid sigmoid neuron saturation
    # Seems like this could really mess with the interpretation of each piece
    # designation?
    vector -= vector.mean()
    vector /= vector.max()

if __name__ == "__main__":
    games = parsePGN(fname)
    for game in games:
        

