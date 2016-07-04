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
empty = 0

piece = {'P':P,'R':R,'N':N,'B':B,'Q':Q,'K':K}
coord = {chr(i):i-97 for i in range(97,105)}

class Game:
    def __init__(self, result, moves):
        self.result = result
        if len(moves) % 2 == 1:
            moves.append(None)
        try:
            self.moves = [(moves[i].split('.')[1],moves[i+1]) for i in range(0, len(moves)-5, 2)]
        except IndexError:
            print moves
        self.result = result.split('-')[0]
        self.board = np.empty((8,8))
        self.board[0] = np.array([R,N,B,Q,K,B,N,R])
        self.board[-1] = Bl*np.array([R,N,B,Q,K,B,N,R])

    def clarifyMove(self, move, team):
        move = move.replace('x','')
        start = [None, None]
        end = [coord[move[-2]], int(move[-1])]

        ##########
        #  PAWN
        ##########

        #move
        if len(move) == 2:
            p = P
            start = [end[0], end[1] - team]
            if self.coord(*start) != team*P:
               start[1] -= team
            return (start, end)
               
        #capture -- does not include en'passant
        if move[0] in coord.keys() and 'x' in move:
               return ([coord[move[0]], end[1] - team], end)


        p = piece[move[0]]

        ##########
        #  ROOK
        ##########

        if p == 'R':
            #move = move.replace('x','')
            starts = []
            for i in range(0,end[0],-1):
                p = self.coord(i, end[1])
                if  p == team*R:
                    starts.append([i, end[1]])
                elif p != empty:
                    break
            for i in range(end[0],8):
               p = self.coord(i, end[1])
               if  p == team*R:
                   starts.append([i, end[1]])
               elif p != empty:
                   break
            for i in range(0,end[1],-1):
               p = self.coord(end[0],i)
               if p == team*R:
                   starts.append([end[0], i])
               elif p != empty:
                   break
            for i in range(end[1],8):
               p = self.coord(end[0],i)
               if p == team*R:
                   starts.append([end[0], i])
               elif p != empty:
                   break
            if len(starts) > 1:
                if len(move) == 4:
                    if starts[0][0] == coord[move[1]]:
                        start = starts[0]
                    else:
                        start = starts[1]
            else:
                start = starts[0]

            ##########
            # KNIGHT
            ##########

            if p == 'N':
                #move = move.replace('x','')
                starts = []
                for i in range(-2,3,4):
                    for j in range(-1,2,2):
                        p1 = self.coord(end[0] + i, end[1] + j)
                        p2 = self.coord(end[0] + j, end[1] + i)
                        if p1 == team*N:
                            starts.append([end[0]+i,end[1]+j])
                        if p2 == team*N:
                            starts.append([end[0]+j,end[1]+i])
                if len(starts) > 1 and len(move) == 4:
                    if starts[0][0] == coord[move[1]]:
                        start = starts[0]
                    else:
                        start = starts[1]
                else:
                    start = starts[0]

            ##########
            # BISHOP
            ##########

            if p == 'B':
                #move = move.replace('x','')
                starts = []
                indices = [0,1,2,3]
                for i in range(1,8):
                    p = [[end[0]+i,end[1]+i],
                         [end[0]-i,end[1]-i],
                         [end[0]-i,end[1]+i],
                         [end[0]+i,end[1]-i]]
                    r = []
                    for i in indices:
                        if self.coord(*p) == team*B:
                            start = p
                        elif self.coord(*p) != empty:
                            r.append(i)
                    indices = [i for i in indices if i not in r]
                            
                    

            #ambiguous
            elif len(move) == 4:
                start[0] = coord[move[0]]
                for i in range(0,end[1],-1):
                    p = self.coord(end[0],i)
                    if p == team*R:
                        return ([end[0], i], end)
                    elif p != empty:
                        break

        return(start,end)

    def coord(self, c1, c2):
        pass

            
games = []
inMoves = False
moves = ''
with open(fname) as pgn:
    for line in pgn.readlines():
        if line[0] == '1':
            inMoves = True
        elif inMoves and line == '\n':
            moves = moves.split()
            #print moves
            games.append(Game(moves[-1], moves[:-1]))
            inMoves = False
            moves = ''
        if inMoves:
            moves += line.replace('\n',' ')
