import numpy as np

fname = 'Adams.pgn'
Wh = 1
Bl = -1
P = 1
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

    def runGame(self, verbose=False):
        '''
        Iterates over the moves pulled from PGN file and plays the game described, 
        printing along the way.
        '''
        # m is a 2-tuple of form (white's move, black's move) in standard chess notation.
        for i, m in enumerate(self.moves):
            if verbose: print(i,m)
            self.movenum += 1

            # Pass in white's move in standard chess notation and white's team 
            # code to extract starting and ending positions.
            startW, endW = self.clarifyMove(m[0], Wh)
            # Update the board
            self.movePiece(startW, endW, Wh)
            
            # Pass in black's move in standard chess notation and black's team 
            # code to extract starting and ending positions.
            startB, endB = self.clarifyMove(m[1], Bl)
            # Update the board
            self.movePiece(startB, endB, Bl)

            if verbose:
                '\n',m
                self.Print()
            

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


    def clarifyMove(self, move, team):
        '''
        move - string containing standard chess notation for the move
        team - corresponds to one of the two team codes
        '''
        # Checks do not affect anything
        move = move.replace('+','')

        start = [None, None]
        
        # If not castling or promoting a pawn, the move ends on the last two 
        # coordinates
        if move != 'O-O' and move != 'O-O-O' and '=' not in move:
            
            # Coordinate in range 1 <= end[i] <= 8
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
            return (start, end)
               
        #capture -- does not include en'passant
        if move[0] in coord.keys():
            if '=' in move:
                if len(move) == 4:
                    return ([coord[move[0]], int(move[1]) - team], [coord[move[0]], int(move[1])])
                else:
                    return ([coord[move[0]], int(move[3]) - team], [coord[move[2]], int(move[3])])

            if 'x' in move:
               return ([coord[move[0]], end[1] - team], end)
        
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
                return ([5,team],[3,team])
            # King-side castling
            else:
                return ([5,team],[7,team])
        return(start,end)

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
            #print("failed",c1,c2)
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

    def movePiece(self, start, end, team):
        '''
        Given a start and end string in standard chess notation and a team 
        distinction, the board gets updated accordingly.
        '''
        #Special case of a promotion (assumes to queen)
        if end[1] == 8 and self.coord(*start) == P or end[1] == 1 and self.coord(*start) == -1*P:
            self.setCoord(end[0], end[1], team*Q)
        else:
            #Replace destination with moving piece
            self.setCoord(end[0], end[1], self.coord(*start))
        
        #Replace starting place with empty
        self.setCoord(start[0], start[1],empty)

        #Handles the rook move in the case of castling
        if self.coord(*end) == team*K and abs(end[0] - start[0]) > 1:
            if end[0] == 7:
                self.setCoord(6, team, team*R)
                self.setCoord(8, team, empty)
            elif end[0] == 3:
                self.setCoord(4, team, team*R)
                self.setCoord(1, team, empty)

    def Print(self):
        ''' Print board in a human-readable format. '''
        remap = {v:'w' + k for k,v in piece.items()}
        remap.update({-v:'b' + k for k,v in piece.items()})
        remap[0] = '  '
        printedBoard = np.zeros((8,8), dtype=object)
        for i in range(8):
            for j in range(8):
                printedBoard[j][i] = remap[self.board[i][j]]
        print('     A    B    C    D    E    F    G    H')
        for i,r in enumerate(printedBoard):
            print(i+1,r)
        print('\n')

def parsePGN(fname):
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
                
            #Middle of a game
            if inMoves:
                moves += line.replace('\n',' ')
                
    return games

if __name__ == "__main__":

    games = parsePGN(fname)
    #games[0].runGame(True)
    tally = 0
    for i,g in enumerate(games):
        if i%100==0: print(i)
        #g.runGame()
        try:
            g.runGame()
            tally += 1
        except IndexError:
            pass
    print(tally / float(len(games)))
