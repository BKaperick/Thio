from read_pgn import *
from chess import *
from play import *
from test import run_tests
from itertools import chain
from sys import argv

'''
COMMAND-LINE options:
py main.py play [White/Black] [game_file]
py main.py play Black
py main.py test
py main.py hist [verbosity]
'''

DEFAULT_SAVE_FILE = 'saved.txt'



mode_to_function = {
        'play': play_game,
        'hist': run_history,
        'test': run_tests}


def parse_input(argv):
    mode_options = ('play','hist','test')
    mode = argv[1].lower()
    other_options = []
    if mode == 'play':
        try:
            team = argv[2][0].lower()
            cp_team = Wh if team == 'b' else Bl
            cp_movemaker = alphabeta_adj_move
            load_file = argv[4] if len(argv) > 4 else None
            save_file = argv[3] if len(argv) > 3 else load_file # Will simply append to the existing file
        except IndexError:
            raise ArgumentError("expected call of form `$python main.py play [team] [load_file] [save_file]")
        other_options = [cp_team, cp_movemaker, load_file, save_file]
    elif mode == "test":
        verbosity = int(argv[2]) if len(argv) > 2 else 0
        other_options = (verbosity,)
    elif mode == "hist":
        fname = "../data/Adams.pgn"
        verbosity = int(argv[2]) if len(argv) > 2 else 0
        other_options = (fname, verbosity)
    return mode, other_options
    
def execute_command(mode, other_options):
    try:
        mode_function = mode_to_function[mode]
        result = mode_function(*other_options)
        return result
    except KeyError:
        raise ArgumentError("not a valid execution mode")

if __name__ == "__main__":
    mode, other_options = parse_input(argv)
    execute_command(mode, other_options)
    
