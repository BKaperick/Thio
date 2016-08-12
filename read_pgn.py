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
coord = {chr(i):i-96 for i in range(97,105)}



class Game:
    def __init__(self, result, moves):
        
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
        for i, m in enumerate(self.moves):
            if verbose:
                print '\n',m
            self.movenum += 1
            team = int(((i % 2) - .5) * 2)
            startW, endW = self.clarifyMove(m[0], Wh)
            self.movePiece(startW, endW, Wh)
            startB, endB = self.clarifyMove(m[1], Bl)
            self.movePiece(startB, endB, Bl)
            if verbose:
                self.Print()
            

    def checkStraights(self, end, team, piece=R):
        starts = []
        for i in range(end[0]-1,0,-1):
            p = self.coord(i, end[1])
            if  p == team*piece:
                starts.append([i, end[1]])
            if p != empty:
                break
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
        starts = []
        indices = [0,1,2,3]
        for i in range(1,8):
            p = [[end[0]+i,end[1]+i],
                 [end[0]-i,end[1]-i],
                 [end[0]-i,end[1]+i],
                 [end[0]+i,end[1]-i]]
            r = []
            if len(indices) == 0:
                break
            for i in indices:
                if self.coord(*(p[i])) == team*piece:
                    starts.append(p[i])
                elif self.coord(*(p[i])) != empty:
                    r.append(i)
            indices = [i for i in indices if i not in r]
        return starts

    def ambiguous(self, starts, move):
        if len(starts) > 1 and len(move) == 4:
                if starts[0][0] == coord[move[1]]:
                    start = starts[0]
                else:
                    start = starts[1]
        else:
            start = starts[0]
        return start


    def clarifyMove(self, move, team):
        move = move.replace('+','')
        start = [None, None]
        if move != 'O-O' and move != 'O-O-O' and '=' not in move:
            end = [coord[move[-2]], int(move[-1])]
        ##########
        #  PAWN
        ##########

        #move
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
        
        elif p == K:
            starts = []
            for i in range(-1,2):
                for j in range(-1,2):
                    crd = [end[0] + i, end[1] + j]
                    if (not (i == 0 and j == 0)) and self.coord(*crd) == team*K:
                        start = crd
                        break 
        #Castling
        elif p == O:
            if len(move) == 5:
                return ([5,team],[3,team])
            else:
                return ([5,team],[7,team])
        return(start,end)

    def coord(self, c1, c2):
        if c1 < 0:
            c1 += 9
        if c2 < 0:
            c2 += 9
        try:
            return self.board[c1-1, c2-1]
        except IndexError:
            return None

    def setCoord(self, c1, c2, val):
        if c1 < 0:
            c1 += 9
        if c2 < 0:
            c2 += 9
        self.board[c1-1, c2-1] = val

    def movePiece(self, start, end, team):
        if end[1] == 8 and self.coord(*start) == P or end[1] == 1 and self.coord(*start) == -1*P:
            self.setCoord(end[0], end[1], team*Q)
        else:
            #Replace destination with moving piece
            self.setCoord(end[0],end[1],self.coord(*start))
        
        #Replace starting place with empty
        self.setCoord(start[0],start[1],empty)

        #Handles the rook move in the case of castling
        if self.coord(*end) == team*K and abs(end[0] - start[0]) > 1:
            if end[0] == 7:
                self.setCoord(6, team, team*R)
                self.setCoord(8, team, empty)
            elif end[0] == 3:
                self.setCoord(4, team, team*R)
                self.setCoord(1, team, empty)

    def Print(self):
        remap = {v:'w' + k for k,v in piece.items()}
        remap.update({-v:'b' + k for k,v in piece.items()})
        remap[0] = '  '
        printedBoard = np.zeros((8,8), dtype=object)
        for i in range(8):
            for j in range(8):
                printedBoard[j][i] = remap[self.board[i][j]]
        print '     A    B    C    D    E    F    G    H'
        for i,r in enumerate(printedBoard):
            print i+1,r

def parsePGN(fname):
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

games = parsePGN(fname)
#games[81].runGame(True)
tally = 0
for i,g in enumerate(games):
    try:
        g.runGame()
        tally += 1
    except IndexError:
        pass
print tally / float(len(games))
