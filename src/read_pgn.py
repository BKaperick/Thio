'''
TODO: Add more data files and seamless reading of multiple files.  (Ideally all .pgn's in ../data directory).
TODO: Handle en'passant by making pawns "fresh pawns" for exactly one move after a double move.
'''

import numpy as np

fname = '../data/Adams.pgn'
Wh = 1
Bl = -1
P = 1

#fP is a "fresh pawn" (one that has just moved two spaces and can be en'passanted next turn.
fP = 8
R = 2
N = 3
B = 4
Q = 5
K = 6
C = 7
O = 7
empty = 0

piece = {'P':P,'R':R,'N':N,'B':B,'Q':Q,'K':K,'O':C}

# a:1, ..., h:8
coord = {chr(i):i-96 for i in range(97,105)}


class Game:
    def __init__(self, result, moves):
        '''
        result - is a string '1' or '0' or '1/2' indicating the game result
        moves - a list of moves alternating between white and black moves given
        in standard chess notation.

        Also builds the board to the initial setup ready for simulation.
        self.board[i,j] is the ith rank (row) and jth file (column), each
        indexed from 0-7
        '''
        
        #Adds null move if white was the last to play
        if len(moves) % 2 == 1:
            moves.append(None)

        #Removes move number from each pair of moves
        self.moves = [(moves[i].split('.')[1],moves[i+1]) for i in range(0, len(moves)-5, 2)]

        self.result = result.split('-')[0]

        #Initializes board to chess starting position
        self.board = np.zeros((8,8), dtype=np.int8)
        self.board[:,0] = np.array([R,N,B,Q,K,B,N,R], dtype=np.int8)
        self.board[:,1] = np.array([P,P,P,P,P,P,P,P], dtype=np.int8)
        self.board[:,-1] = Bl*np.array([R,N,B,Q,K,B,N,R], dtype=np.int8)
        self.board[:,-2] = Bl*np.array([P,P,P,P,P,P,P,P], dtype=np.int8)

        self.movenum = 0

    def runGame(self, savestates=True, verbose=0):
        '''
        Iterates over the moves pulled from PGN file and plays the game described, 
        printing along the way.

        If savestates is True, the board is deep-copied after each board change.
        If verbose is True, the board is printed after each black move.
        '''
        states = [self.board.copy()]
        startB, endB = '', ''
        
        # m is a 2-tuple of form (white's move, black's move) in standard chess notation.
        for i, m in enumerate(self.moves):
            if verbose: print(i,m)
            self.movenum += 1

            # Pass in white's move in standard chess notation and white's team 
            # code to extract starting and ending positions.
            (startW, endW), enpassant_flag = self.clarifyMove(m[0], Wh, startB, endB)
            print(startW, endW, enpassant_flag)
            
            # Update the board
            self.movePiece(startW, endW, Wh, enpassant=enpassant_flag)
            
            if savestates:
                states.append(self.board.copy())
            
            # Pass in black's move in standard chess notation and black's team 
            # code to extract starting and ending positions.
            (startB, endB), enpassant_flag = self.clarifyMove(m[1], Bl, startW, endW)
            print(startW, endW, enpassant_flag)
            
            # Update the board
            self.movePiece(startB, endB, Bl, enpassant=enpassant_flag)
            
            if savestates:
                states.append(self.board.copy())
            
            if verbose >= 2:
                print("\n", m)
                print_board(self.board)
        
        if savestates:
            return states
            

    def checkStraights(self, end, team, piece=R):
        '''
        Given an end coordinate on range [1,8] and a team/piece, returns a list 
        of all pieces of this team and this piece type which could have reached 
        end with a straight movement.
        '''
        starts = []

        # Row to left of end coordinate
        for i in range(end[0]-1,0,-1):
            p = self.coord(i, end[1])
            if  p == team*piece:
                starts.append([i, end[1]])
            if p != empty:
                break
        
        # Row to right of end coordinate
        for i in range(end[0]+1,9):
            p = self.coord(i, end[1])
            if  p == team*piece:
                starts.append([i, end[1]])
            if p != empty:
                break
        for i in range(end[1]-1,0,-1):
            p = self.coord(end[0],i)
            if p == team*piece:
                starts.append([end[0], i])
            if p != empty:
                break
        for i in range(end[1]+1,9):
            p = self.coord(end[0],i)
            if p == team*piece:
                starts.append([end[0], i])
            if p != empty:
                break
        return starts


    def checkDiags(self, end, team, piece=B):
        '''
        Given an end coordinate and a team/piece, returns a list of all pieces
        of this team and this piece type which could have reached end with a 
        diagonal movement.
        '''
        starts = []
        indices = [0,1,2,3]
        for i in range(1,8):
            p = [[end[0]+i,end[1]+i],
                 [end[0]-i,end[1]-i],
                 [end[0]-i,end[1]+i],
                 [end[0]+i,end[1]-i]]
            
            # Remove diagonal check if a wall is hit
            indices = [i for i in indices if all([1 <= y <= 8 for y in p[i]])] 

            r = []

            # If all avenues have been checked
            if len(indices) == 0:
                break
            for i in indices:
                if self.coord(*(p[i])) == team*piece:
                    starts.append(p[i])
                    r.append(i) 
                elif self.coord(*(p[i])) != empty:
                    r.append(i)
            indices = [i for i in indices if i not in r]
        return starts

    
    def ambiguous(self, starts, move):
        '''
        starts is a list returned from checkStraights() or checkDiags() 
        which contains a list of coordinates of pieces which could make 
        the inputted move.
        '''
        # If there are multiple options and move supposes there should be no
        # ambiguity by only listing two coordinates (4 characters)
        if len(starts) > 1 and len(move) == 4:
                if starts[0][0] == coord[move[1]]:
                    start = starts[0]
                else:
                    start = starts[1]
        
        # Simply return the only element from starts if len(starts) == 1, 
        # Or return the first element from starts (sloppy handling).
        else:
            start = starts[0]

        return start


    def clarifyMove(self, move, team, prev_move_start, prev_move_end):
        '''
        move - string containing standard chess notation for the move
        team - corresponds to one of the two team codes

        Returns a 2-tuple of the moving pieces
        '''
        # Checks do not affect anything
        move = move.replace('+','')

        start = [None, None]
        
        # If not castling or promoting a pawn, the move ends on the last two 
        # coordinates
        if move != 'O-O' and move != 'O-O-O' and '=' not in move:
            
            # Note this coordinate is in range 1 <= end[i] <= 8
            end = [coord[move[-2]], int(move[-1])]

        ##########
        #  PAWN
        ##########

        # If the move consists of two coordinates, it's a pawn
        if len(move) == 2:
            p = P
            
            start = [end[0], end[1] - team]

            #If start is incorrect
            if self.coord(*start) != team*P:
               start[1] -= team
            return (start, end), False
               
        #capture -- does not include en'passant
        if move[0] in coord.keys():
            if '=' in move:
                if len(move) == 4:
                    return ([coord[move[0]], int(move[1]) - team], [coord[move[0]], int(move[1])]), False
                else:
                    return ([coord[move[0]], int(move[3]) - team], [coord[move[2]], int(move[3])]), False

            if 'x' in move:
                output = ([coord[move[0]], end[1] - team], end)
                # En'passant
                if coord[move[2]] == prev_move_start[0] == prev_move_end[0] and prev_move_end[1] + team == end[1]:
                   return output, True 
                return output, False
        
        # Do not need to know if a piece is being taken
        move = move.replace('x','')
        
        p = piece[move[0]]

        ##########
        #  ROOK
        ##########

        if p == R:
            starts = self.checkStraights(end, team)
            if len(move) == 4:
                if move[1] in coord.keys():
                    starts = [m for m in starts if m[0] == coord[move[1]]]
                else:
                    starts = [m for m in starts if m[1] == int(move[1])]
            start = self.ambiguous(starts, move)


        ##########
        # KNIGHT
        ##########

        elif p == N:
            starts = []
            for i in range(-2,3,4):
                for j in range(-1,2,2):
                    p1 = self.coord(end[0] + i, end[1] + j)
                    p2 = self.coord(end[0] + j, end[1] + i)
                    if p1 == team*N:
                        starts.append([end[0]+i,end[1]+j])
                    if p2 == team*N:
                        starts.append([end[0]+j,end[1]+i])

            #If additional context is needed to clarify
            if len(move) == 4:
                if move[1] in coord.keys():
                    starts = [m for m in starts if m[0] == coord[move[1]]]
                else:
                    starts = [m for m in starts if m[1] == int(move[1])]
            start = self.ambiguous(starts, move)


        ##########
        # BISHOP
        ##########

        elif p == B:
            starts = self.checkDiags(end, team)
            start = self.ambiguous(starts, move)
            

        ##########
        # QUEEN
        ##########

        elif p == Q:
            starts = self.checkStraights(end, team, piece=Q)
            starts += self.checkDiags(end, team, piece=Q)
            start = self.ambiguous(starts, move)


        ##########
        #  KING
        ##########
                
        elif p == K: # Piece is equal to "king"
            starts = [] # init starts
            for i in range(-1,2): 
                for j in range(-1,2):
                    crd = [end[0] + i, end[1] + j] # Relative coordinates (-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)

                    # If we exclude (0,0) and 
                    if (not (i == 0 and j == 0)) and self.coord(*crd) == team*K:
                        start = crd
                        break 
        #Castling
        elif p == O:
            # Queen-side castling
            if len(move) == 5:
                return ([5,team],[3,team]), False
            # King-side castling
            else:
                return ([5,team],[7,team]), False

        return(start,end), False

    def coord(self, c1, c2):
        '''
        Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
        the specified board position.  Negative indices are treated such that 
        -1 maps to 8, -2 maps to 7, etc.  This functionality is only used when
        handling castling and promotions symmetrically.
        
        c1==0 and c2==0 are due to checkStraights() or checkDiags() testing a 
        position which is out of bounds, so None is returned.
        '''
        if c1==0 or c2==0: return None
        if c1 < 0: c1 += 9
        if c2 < 0: c2 += 9
        try:
            return self.board[c1-1, c2-1]
        except IndexError:
            return None

    #Sets the board position to val
    def setCoord(self, c1, c2, val):
        '''
        Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
        the specified board position and updates self.board with val at this 
        position.  Negative indices are treated such that -1 maps to 8, -2 maps
        to 7, etc.  This functionality is only used when
        handling castling and promotions symmetrically.
        
        c1==0 and c2==0 are due to checkStraights() or checkDiags() testing a 
        position which is out of bounds, so None is returned.
        '''
        if c1 < 0: c1 += 9
        if c2 < 0: c2 += 9
        self.board[c1-1, c2-1] = val

    def movePiece(self, start, end, team, enpassant = False):
        '''
        Given a start and end coordinates (2-lists) and a team 
        distinction, the board gets updated accordingly.
        '''
        # Regardless of any other movements, all fresh pawns are converted to regular pawns.
        for x,y in zip(*np.where(self.board*team > 0)):
            if self.board[x,y] == team*fP:
                self.board[x,y] = team*P

        #Special case of a promotion (assumes to queen)
        if end[1] == 8 and self.coord(*start) == P or end[1] == 1 and self.coord(*start) == -P:
            self.setCoord(*end, team*Q)
        else:
            # In the case of double-moving pawn (special case to allow en'passant on it)
            if self.coord(*start) == team*P and abs(end[1] - start[1]) == 2:
                self.setCoord(*end, team*fP)

            # All other basic moves
            else:
                self.setCoord(*end, self.coord(*start))
        
            #Replace destination with moving piece
            self.setCoord(*end, self.coord(*start))
        
        # Remove the pawn that has been en'passanted
        if enpassant:
            self.setCoord(end[0], end[1] - team, empty)
        
        #Replace starting place with empty
        self.setCoord(*start, empty)

        #Handles the rook move in the case of castling
        if self.coord(*end) == team*K and abs(end[0] - start[0]) > 1:
            if end[0] == 7:
                self.setCoord(6, team, team*R)
                self.setCoord(8, team, empty)
            elif end[0] == 3:
                self.setCoord(4, team, team*R)
                self.setCoord(1, team, empty)

def print_board(board):
    ''' Print board in a human-readable format. '''
    remap = {v:'w' + k for k,v in piece.items()}
    remap.update({-v:'b' + k for k,v in piece.items()})
    remap[0] = '  '
    printedBoard = np.zeros((8,8), dtype=object)
    for i in range(8):
        for j in range(8):
            printedBoard[j][i] = remap[board[i][j]]
    print('     A    B    C    D    E    F    G    H')
    for i,r in enumerate(printedBoard):
        print(i+1,r)
    print('\n')

def parsePGN(fname, max_count = 0):
    '''
    Take in a string file location fname and return a list of games.
    Games list is comprised of Game objects.
    '''
    games = []
    inMoves = False
    moves = ''
    with open(fname) as pgn:
        for line in pgn.readlines():
            
            #Start of a game
            if line[0] == '1':
                inMoves = True
             
            #End of a game
            elif inMoves and line == '\n':
                moves = moves.split()

                #Create game object from moves
                games.append(Game(moves[-1], moves[:-1]))
                inMoves = False
                moves = ''
                
                if len(games) == max_count:
                    break
                
            #Middle of a game
            if inMoves:
                moves += line.replace('\n',' ')
            
    
    return games

def only_correct_games(fname, games):
    '''
    Returns a filtered list of games which can be parsed correctly and 
    completely by Game.runGame().

    Technically, the standard this function checks is that Game.runGame()
    completes without an index error, so it is possible there is still some
    amount of incorrectness in the Game code.
    '''
    
    # Identifies games which run without error
    correct_game_indices = []
    for i,g in enumerate(games):
        try:
            g.runGame()
            correct_game_indices.append(i)
        except IndexError:
            pass
    
    # The error check code calls runGame() which can only be called once per
    # game, so they must be regenerated.
    fresh_games = parsePGN(fname)
    correct_fresh_games = [x for i,x in enumerate(fresh_games) if i in correct_game_indices]
    return correct_fresh_games

#def clean_file(fname, indices):
#    '''
#    Reads fname and 
#    '''
#    new_fname = fname[:-4] + "_corrected_.pgn"
#    with open(fname) as f:
#        with open(new_fname, "w") as new_f:
            


if __name__ == "__main__":

    games = only_correct_game_indices(fname, parsePGN(fname))
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
