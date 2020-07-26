import numpy as np
from chess import *

Wh = 1
Bl = -1

#fP is a "fresh pawn" (one that has just moved two spaces and can be 
# en'passanted next turn.
P = 1
fP = 8
R = 2
N = 3
B = 4
Q = 5
K = 6
C = 7
O = 7
empty = 0

piece = {'F':fP,'P':P,'R':R,'N':N,'B':B,'Q':Q,'K':K,'O':C}
reversePiece = {v:k for k,v in piece.items()}

# a:1, ..., h:8
rankLetterToCol = {chr(i):i-96 for i in range(97,105)}
colToRankLetter = {v:k for k,v in rankLetterToCol.items()}

class Game:
    def __init__(self, cpTeam, movemaker):
        '''
        INPUT
        result -- a string '1' or '0' or '1/2' indicating the game result
        moves -- a list of moves alternating between white and black moves each 
        given as a string of standard chess notation.

        RETURN
        self -- Game instance

        Also builds the board to the initial setup ready for simulation.
        self.board[i,j] is the ith rank (row) and jth file (column), each
        indexed from 0-7
        '''
        self.result = ''
        self._cpTeam = cpTeam
        self._movemaker = movemaker

        #Initializes board to chess starting position
        self.createCleanBoard()

        self.movenum = 0

    def getNextMove(self,before,after,team):
        if team == self._cpTeam:
            return self.getNextComputerMove(team)
        else:
            return self.getNextUserMove(before,after,team)

    def getNextUserMove(self,before,after,team):
        move = input("move:")
        return self.clarifyMove(move, team, before, after)

    def getNextComputerMove(self,team):
        return self._movemaker(self.board,self._cpTeam)
    
    def runGame(self, savestates=True, verbose=0):
        '''
        INPUT
        savestates -- if is True, the board is deep-copied after each board change.
        verbose -- if is True, the board is printed after each black move.
        
        Iterates over the moves pulled from PGN file and plays the game described, 
        printing along the way.

        RETURN
        states -- if savestates is True, an array of board states detailing the 
            history of the game, else None
        '''
        states = [self.board.copy()]
        startB, endB = '', ''
        
        # m is a 2-tuple of form (white's move, black's move) in standard chess notation.
        while True:
            self.movenum += 1
            
            (startW,endW) = self.makeMove(startB,endB,Wh)
            
            if savestates:
                states.append(self.board.copy())

            (startB,endB) = self.makeMove(startW,endW,Bl)

            if savestates:
                states.append(self.board.copy())
            
            
            if verbose >= 0:
                #print("\nmoves:", startW,endW,"\n",startB,endB)
                print_board(self.board,perspective=-self._cpTeam)
        
        if savestates:
            return states
            

    def createCleanBoard(self):
        self.board = np.zeros((8,8), dtype=np.int8)
        self.board[:,0] = np.array([R,N,B,Q,K,B,N,R], dtype=np.int8)
        self.board[:,1] = np.array([P,P,P,P,P,P,P,P], dtype=np.int8)
        self.board[:,-2] = Bl*np.array([P,P,P,P,P,P,P,P], dtype=np.int8)
        self.board[:,-1] = Bl*np.array([R,N,B,Q,K,B,N,R], dtype=np.int8)
    
    def makeMove(self, prevTurnStart, prevTurnEnd, team):
        
        # code to extract starting and ending positions.
        (boardTurnStart, boardTurnEnd), enpassant_flag = self.getNextMove(prevTurnStart,prevTurnEnd,team)
        # update board
        self.movePiece(boardTurnStart, boardTurnEnd, team, enpassant=enpassant_flag)
        return boardTurnStart, boardTurnEnd

    def checkStraights(self, end, team, piece=R):
        '''
        Given an end coordinate (row,col) on range [1,8] and a team/piece, returns a list 
        of all pieces of this team and this piece type which could have reached 
        end with a straight movement.
        '''
        starts = []

        # Row to left of end coordinate
        for i in range(end[1]-1,0,-1):
            p = self.coord(end[0], i)
            if  p == team*piece:
                starts.append([end[0], i])
            if p != empty:
                break
        
        # Row to right of end coordinate
        for i in range(end[1]+1,9):
            p = self.coord(end[0], i)
            if  p == team*piece:
                starts.append([end[0], i])
            if p != empty:
                break
        for i in range(end[0]-1,0,-1):
            p = self.coord(i, end[1])
            if p == team*piece:
                starts.append([i, end[1]])
            if p != empty:
                break
        for i in range(end[0]+1,9):
            p = self.coord(i, end[1])
            if p == team*piece:
                starts.append([i, end[1]])
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
                if starts[0][0] == rankLetterToCol[move[1]]:
                    start = starts[0]
                else:
                    start = starts[1]
        elif len(starts) > 1 and len(move) == 3 and move[0] == 'N':
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
        prev_move_start - 
        prev_move_end - 

        Returns a 2-tuple of the moving pieces
        '''
        print("clarify:",move)
        #print("cm: ", move)
        # Checks do not affect anything
        move = move.replace('+','')

        start = [None, None]
        
        # If not castling or promoting a pawn, the move ends on the last two 
        # coordinates
        if move != 'O-O' and move != 'O-O-O' and '=' not in move:
            
            # Note this coordinate is in range 1 <= end[i] <= 8
            # and end[0] is a file
            # and end[1] is a rank
            end = [int(move[-1]), rankLetterToCol[move[-2]]]

        ##########
        #  PAWN
        ##########

        # If the move consists of two coordinates, it's a pawn
        if len(move) == 2:
            p = P
            
            start = [end[0] - team, end[1]]

            #If start is incorrect
            if self.coord(*start) != team*P and self.coord(*start) != team*fP:
               start[0] -= team
            return (start, end), False
               
        #capture -- does not include en'passant
        if move[0] in coord.keys():
            if '=' in move:
                if len(move) == 4:
                    return ([int(move[1]) - team, rankLetterToCol[move[0]]], [int(move[1]), rankLetterToCol[move[0]]]), False
                else:
                    return ([int(move[3]) - team, rankLetterToCol[move[0]]], [int(move[3]), rankLetterToCol[move[2]]]), False

            if 'x' in move:
                if len(move) == 5:
                    move = move.replace('x','')
                output = ([end[1] - team, rankLetterToCol[move[0]]], end)
                # En'passant
                if rankLetterToCol[move[2]] == prev_move_start[1] == prev_move_end[1] and prev_move_end[0] + team == end[0]:
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
                if move[1] in rankLetterToCol.keys():
                    starts = [m for m in starts if m[0] == rankLetterToCol[move[1]]]
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
                if move[1] in rankLetterToCol.keys():
                    starts = [m for m in starts if m[1] == rankLetterToCol[move[1]]]
                else:
                    starts = [m for m in starts if m[0] == int(move[1])]
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
            for direction in lrup + diags:
                crd = [end[0] + direction[0], end[1] + direction[1]] # Relative coordinates (-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)

                if self.coord(*crd) == team*K:
                    start = crd
                    break 
        #Castling
        elif p == O:
            # Queen-side castling
            if len(move) == 5:
                return ([team,5],[team,3]), False
            # King-side castling
            else:
                return ([team,5],[team,7]), False

        return(start,end), False

    def coord(self, c1, c2):
        '''
        INPUT
        row,col
        Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
        the specified board position.  Negative indices are treated such that 
        -1 maps to 8, -2 maps to 7, etc.  This functionality is only used when
        handling castling and promotions symmetrically.
        
        c1==0 and c2==0 are due to checkStraights() or checkDiags() testing a 
        position which is out of bounds, so None is returned.

        c1 is a file
        c2 is a rank
        '''
        if c1==0 or c2==0: return None
        if c1 < 0: c1 += 9
        if c2 < 0: c2 += 9
        try:
            return self.board[c2-1, c1-1]
        except IndexError:
            return None

    def movePiece(self, start, end, team, enpassant = False):
        '''
        Given a start and end coordinates (2-lists) and a team 
        distinction, the board gets updated accordingly.
        '''
        #print("mp: ",start, end, team, enpassant)
        #print_board(self.board)
        # Regardless of any other movements, all fresh pawns are converted to regular pawns.
        for x,y in zip(*np.where(self.board*team > 0)):
            if self.board[x,y] == team*fP:
                self.board[x,y] = team*P
        
        #Special case of a promotion (assumes to queen)
        if end[0] == 8 and self.coord(*start) == P or end[0] == 1 and self.coord(*start) == -P:
            setCoord(self.board, *end, team*Q)
        else:
            # In the case of double-moving pawn (special case to allow en'passant on it)
            if self.coord(*start) == team*P and abs(end[0] - start[0]) == 2:
                setCoord(self.board, *end, team*fP)

            # All other basic moves
            else:
                #Replace destination with moving piece
                setCoord(self.board, *end, self.coord(*start))
        
        # Remove the pawn that has been en'passanted
        if enpassant:
            setCoord(self.board, end[1], end[0] - team, empty)
        
        #Replace starting place with empty
        setCoord(self.board, *start, empty)

        #Handles the rook move in the case of castling
        if self.coord(*end) == team*K and abs(end[1] - start[1]) > 1:
            if end[1] == 7:
                setCoord(self.board, team, 6, team*R)
                setCoord(self.board, team, 8, empty)
            elif end[1] == 3:            
                setCoord(self.board, team, 4, team*R)
                setCoord(self.board, team, 1, empty)

# Helper functions

def print_board(board,perspective = Bl):
    ''' Print board in a human-readable format. '''
    remap = {v:'w' + k for k,v in piece.items()}
    remap.update({-v:'b' + k for k,v in piece.items()})
    remap[0] = '  '
    printedBoard = np.zeros((8,8), dtype=object)
    for i in range(8):
        for j in range(8):
            if perspective == Wh:
                printedBoard[7-j][i] = remap[board[i][j]]
            else:
                printedBoard[j][7-i] = remap[board[i][j]]
    if perspective == Wh:
        print('     A    B    C    D    E    F    G    H')
    else:
        print('A    B    C    D    E    F    G    H    '[::-1])
    for i,r in enumerate(printedBoard):
        if perspective == Wh:
            print(8-i,r)
        else:
            print(i+1,r)
    print('\n')

def translateMoveToChessNotation(move):
    piece = reversePiece[move[0]]
    if piece == 'P':
        piece = ''
    row = move[3]
    col = colToRankLetter[move[4]]
    return piece + str(col) + str(row)

def setCoord(board, c1, c2, val):
    '''
    INPUT is in (row,col) format
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
    board[c2-1, c1-1] = val
    return board
