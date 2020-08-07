import numpy as np
from chess import *

# a:1, ..., h:8
rankLetterToCol = {chr(i):i-96 for i in range(97,105)}
colToRankLetter = {v:k for k,v in rankLetterToCol.items()}

class Game:
    def __init__(self, cpTeam, movemaker, verbosity = 0, savestates = True):
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
        self.savestates = True
        self.states = []

        self.verbose = verbosity

    def getNextMove(self,team):
        if team == self._cpTeam:
            move = self.getNextComputerMove(team)
        else:
            move = self.getNextUserMove(team)
        print("move: ", print_coord(move[0][0]),print_coord(move[0][1]))
        return move

    def getNextUserMove(self, team):
        move = input("move:")
        candidate = self.parseMove(move, team)
        while candidate[0][0][0] == None or candidate[0][0][1] == None or candidate[0][1][0] == None or candidate[0][1][0] == None:
            move = input("Didn't understand, try again.\n\nmove:")
            candidate = self.parseMove(move,team)
        return candidate

    def getNextComputerMove(self, team):
        return self._movemaker(self.board,self._cpTeam,self.movenum)
    
    def runGame(self):
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
        self.createCleanBoard()

        #self.states.append(self.board.copy())
        if self.verbose > 0:
            print_board(self.board,perspective=-self._cpTeam)
        # m is a 2-tuple of form (white's move, black's move) in standard chess notation.
        not_finished = True
        while not_finished:
            self.saveState()
            self.movenum += 1
            
            not_finished = self.makeMove(Wh)
            if not not_finished:
                break
            self.saveState()
            if self.verbose > 0:print_board(self.board,perspective=-self._cpTeam)
            not_finished = self.makeMove(Bl)
    
            if self.verbose > 0:print_board(self.board,perspective=-self._cpTeam)
        print("finished game after",self.movenum,"moves")         


    def createCleanBoard(self):
        self.board = np.zeros((8,8), dtype=np.int8)
        self.board[:,0] = np.array([R,N,B,Q,K,B,N,R], dtype=np.int8)
        self.board[:,1] = np.array([P,P,P,P,P,P,P,P], dtype=np.int8)
        self.board[:,-2] = Bl*np.array([P,P,P,P,P,P,P,P], dtype=np.int8)
        self.board[:,-1] = Bl*np.array([R,N,B,Q,K,B,N,R], dtype=np.int8)
    
    def makeMove(self, team):
        
        # code to extract starting and ending positions.
        reponse = self.getNextMove(team)
        if not reponse:
            return False
        (boardTurnStart, boardTurnEnd), enpassant_flag, promotion_flag = reponse
        if self.verbose > 1:
            print("en passant?", enpassant_flag)
            print("promotion?", promotion_flag)
        # update board
        movePiece(self.board, boardTurnStart, boardTurnEnd, team, enpassant=enpassant_flag, promotion=promotion_flag)
        return True

    def saveState(self):
        if self.savestates:
            self.states.append(self.board.copy())

    def checkStraights(self, end, team, piece=R):
        '''
        Given an end coordinate (row,col) on range [1,8] and a team/piece, returns a list 
        of all pieces of this team and this piece type which could have reached 
        end with a straight movement.
        '''
        starts = []

        # Row to left of end coordinate
        for i in range(end[1]-1,0,-1):
            p = on_board_wraparound(self.board, end[0], i)
            if  p == team*piece:
                starts.append([end[0], i])
            if p != empty:
                break
        
        # Row to right of end coordinate
        for i in range(end[1]+1,9):
            p = on_board_wraparound(self.board, end[0], i)
            if  p == team*piece:
                starts.append([end[0], i])
            if p != empty:
                break
        for i in range(end[0]-1,0,-1):
            p = on_board_wraparound(self.board, i, end[1])
            if p == team*piece:
                starts.append([i, end[1]])
            if p != empty:
                break
        for i in range(end[0]+1,9):
            p = on_board_wraparound(self.board, i, end[1])
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
                if on_board_wraparound(self.board, *(p[i])) == team*piece:
                    starts.append(p[i])
                    r.append(i) 
                elif on_board_wraparound(self.board, *(p[i])) != empty:
                    r.append(i)
            indices = [i for i in indices if i not in r]
        return starts

    
    def ambiguous(self, starts, move):
        '''
        starts is a list returned from checkStraights() or checkDiags() 
        which contains a list of coordinates of pieces which could make 
        the inputted move.
        '''
        # Simply return the only element from starts if len(starts) == 1, 
        # Or return the first element from starts (sloppy handling).
        if len(starts) > 1:
            print("[WARNING] Throwing away moves! ", starts[1:])

        return starts[0]


    def parseMove(self, move, team):
        '''
        move - string containing standard chess notation for the move
        team - corresponds to one of the two team codes
        prev_move_start - 
        prev_move_end - 

        Returns a 2-tuple of the moving pieces
        '''
        if self.verbose > 0: print("[PARSING] ", teams[team], " plays ", move)
        # Checks do not affect anything
        move = move.replace(' ','')
        move = move.replace('+','')
        move = move.replace('-','')
        move = move.replace('#','')
        move = move.replace('0','O')
        move = move.replace('o','O')
        move = move.replace('X','')
        move = move.replace('x','')
        move = move.replace('P','') # pawn moves never need to be referred to with 'P'
        
        #Castling
        if move == 'OO' or move == 'OOO':
            # Queen-side castling
            if len(move) == 3:
                return ([team,5],[team,3]), False, None
            # King-side castling
            else:
                return ([team,5],[team,7]), False, None
        
        piece = None
        start_coord = []
        end_coord = []
        promotion_flag = None
        enpassant_flag = False
        
        # For a promotion, save the result and parse as a normal move after that
        if '=' in move:
            promotion_flag = pieceStrToVal[move[-1]]
            move = move[:-2]
        
        # Pawn move
        if len(move) == 2:
            piece = P
            start_coord = move[0]
            end_coord = move.lower()

        elif len(move) == 3:
            
            # pawn move
            if move.islower():
                piece = P
                start_coord = move[0] + str(int(move[2]) - team)
            
            # piece move
            else: 
                piece = pieceStrToVal[move[0].upper()]
                start_coord = []

            end_coord = move[1:].lower()
        
        elif len(move) == 4:

            # pawn move
            if move[1].isnumeric() and move[0].islower():
                piece = P
                start_coord = move[0:2].lower()

            # piece move
            else:
                piece = pieceStrToVal[move[0].upper()]
                start_coord = move[1]
            end_coord = move[2:].lower()

        # fully explicit move
        elif len(move) == 5:
            piece = pieceStrToVal[move[0].upper()]
            start_coord = move[1:3].lower()
            end_coord = move[3:].lower()
        
        # We should not use `move` after this point

        start = [None,None]
        end = [None,None]
        if len(start_coord) == 1: 
            if start_coord in rankLetterToCol.keys():
                start[1] = rankLetterToCol[start_coord]
            else:
                start[0] = int(start_coord)
        if len(start_coord) == 2: 
            start = [int(start_coord[1]), rankLetterToCol[start_coord[0]]]
        if len(end_coord) == 2:
            end = [int(end_coord[1]), rankLetterToCol[end_coord[0]]]

        if piece != P and all(start) and all(end):
            return (start,end),False,promotion_flag
        
        if self.verbose>1:
            print("pre start: ", start)
            print("pre end: ", end)
        
        ##########
        #  PAWN
        ##########

        if piece == P: 
            start_row = start[0] if start[0] else end[0] - team
            start = [start_row,rankLetterToCol[start_coord[0]]]
            # we always have at least start[1] for a pawn move

            # attack
            if start[1] != end[1]:
                fresh_pawn_expected = [end[0]-team,end[1]]
                enpassant_flag = on_board_wraparound(self.board, *fresh_pawn_expected) * team == -fP

            # possible double move
            else:
                piece_on_board = on_board_wraparound(self.board, *start)
                if piece_on_board != team*P and piece_on_board != team*fP:
                    start[0] -= team
            
               
        ##########
        #  ROOK
        ##########

        elif piece == R:
            starts = self.checkStraights(end, team)
            # indicates ambiguous move like Rce4
            if any(start):
                if start[1] == None: #Rce4
                    starts = [m for m in starts if m[0] == start[0]]
                else: #R1e4
                    starts = [m for m in starts if m[1] == start[1]]
            start = self.ambiguous(starts, move)


        ##########
        # KNIGHT
        ##########

        elif piece == N:
            starts = []
            for i in range(-2,3,4):
                for j in range(-1,2,2):
                    p1 = on_board_wraparound(self.board, end[0] + i, end[1] + j)
                    p2 = on_board_wraparound(self.board, end[0] + j, end[1] + i)
                    if p1 == team*N:
                        starts.append([end[0]+i,end[1]+j])
                    if p2 == team*N:
                        starts.append([end[0]+j,end[1]+i])
            
            # Filter possibilities if more context is given
            if any(start):
                if start[1] == None:
                    starts = [m for m in starts if m[0] == start[0]]
                else:
                    starts = [m for m in starts if m[1] == start[1]]
            start = self.ambiguous(starts, move)


        ##########
        # BISHOP
        ##########

        elif piece == B:
            starts = self.checkDiags(end, team)
            start = self.ambiguous(starts, move)
            

        ##########
        # QUEEN
        ##########

        elif piece == Q:
            starts = self.checkStraights(end, team, piece=Q)
            starts += self.checkDiags(end, team, piece=Q)
            start = self.ambiguous(starts, move)


        ##########
        #  KING
        ##########
                
        elif piece == K: # Piece is equal to "king"
            starts = [] # init starts
            for direction in lrup + diags:
                crd = [end[0] + direction[0], end[1] + direction[1]] # Relative coordinates (-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)

                if on_board_wraparound(self.board, *crd) == team*K:
                    start = crd
                    break 
        if self.verbose > 1:
            print("start: ", start)
            print("end: ", end)
            print("flags: ", enpassant_flag, promotion_flag)
        return(start,end), enpassant_flag, promotion_flag

# Helper functions
def movePiece(board, start, end, team, enpassant = False, promotion = None):
    '''
    Given a start and end coordinates (2-lists) and a team 
    distinction, the board gets updated accordingly.
    '''
    
    # Regardless of any other movements, all fresh pawns are converted to regular pawns.
    for x,y in zip(*np.where(board*team > 0)):
        if board[x,y] == team*fP:
            board[x,y] = team*P
    
    #Special case of a promotion 
    if end[0] == 8 and on_board_wraparound(board, *start) == P or end[0] == 1 and on_board_wraparound(board, *start) == -P:
        setCoord(board, *end, team*promotion)
    else:
        # In the case of double-moving pawn (special case to allow en'passant on it)
        if on_board_wraparound(board, *start) == team*P and abs(end[0] - start[0]) == 2:
            setCoord(board, *end, team*fP)

        # All other basic moves
        else:
            #Replace destination with moving piece
            setCoord(board, *end, on_board_wraparound(board, *start))
    
    # Remove the pawn that has been en'passanted
    if enpassant:
        setCoord(board, end[0] - team, end[1], empty)
    
    #Replace starting place with empty
    setCoord(board, *start, empty)

    #Handles the rook move in the case of castling
    if on_board_wraparound(board,*end) == team*K and abs(end[1] - start[1]) > 1:
        if end[1] == 7:
            setCoord(board, team, 6, team*R)
            setCoord(board, team, 8, empty)
        elif end[1] == 3:            
            setCoord(board, team, 4, team*R)
            setCoord(board, team, 1, empty)

def on_board_wraparound(board, c1, c2):
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
        return on_board(board,c1,c2)
    except IndexError:
        return None

def print_board(board,perspective = Bl):
    ''' Print board in a human-readable format. '''
    remap = {v:'w' + k for k,v in pieceStrToVal.items()}
    remap.update({-v:'b' + k for k,v in pieceStrToVal.items()})
    remap[0] = '  '
    printedBoard = np.zeros((8,8), dtype=object)
    for i in range(8):
        for j in range(8):
            if perspective == Wh:
                printedBoard[7-j][i] = remap[board[i][j]]
            else:
                printedBoard[j][7-i] = remap[board[i][j]]
    row_header = 'A    B    C    D    E    F    G    H'
    if perspective == Wh:
        print(" "*4+row_header)
    else:
        print(" "*4+row_header[::-1])
    for i,r in enumerate(printedBoard):
        if perspective == Wh:
            print(8-i,r)
        else:
            print(i+1,r)
    print('\n')

def translateMoveToChessNotation(move):
    piece = pieceValToStr[move[0]]
    if piece == 'P':
        piece = ''
    row = move[3]
    col = colToRankLetter[move[4]]
    return piece + str(col) + str(row)

def setCoord(board, row, col, val):
    '''
    INPUT is in (row,col) format
    Maps two coordinates on the union of [-8,-1] U [1,8] to the piece at
    the specified board position and updates self.board with val at this 
    position.  Negative indices are treated such that -1 maps to 8, -2 maps
    to 7, etc.  This functionality is only used when
    handling castling and promotions symmetrically.
    
    row==0 and col==0 are due to checkStraights() or checkDiags() testing a 
    position which is out of bounds, so None is returned.
    '''
    if row < 0: row += 9
    if col < 0: col += 9
    board[col-1, row-1] = val
    return board

def print_coord(coord):
    out = colToRankLetter[coord[1]] + str(coord[0])
    return out

def print_move(move):
    if move == None:
        return ""
    return pieceValToStr[move[0]] + print_coord(move[1:3]) + " " + print_coord(move[3:5])

def iterate_board(board):
    for _c,col in enumerate(board):
        for _r,row in enumerate(col):
            r = _r+1
            c = _c+1
            yield on_board(board,r,c),r,c

def board_to_string(board,team):
    board_str = teams[team][0]
    for p,x,y in iterate_board(board):
        if p != empty:
            piece = abs(p)
            team = teams[p][0]
            piece_str = pieceValToStr[piece]
            board_str += team + piece_str + str(x) + str(y)
    return board_str

def string_to_board(board_str):
    turn = teamStrToVal[board_str[0]]
    board = np.zeros((8,8), dtype=np.int8)
    #turn = Wh if board_str[0] == 'W' else Bl
    for i,x in enumerate(board_str[1::4]):
        index = 4*i + 2
        team = teamStrToVal[x]
        piece = pieceStrToVal[board_str[index]]
        row = int(board_str[index+1])
        col = int(board_str[index+2])
        setCoord(board, row, col, team*piece)
    return board, turn



