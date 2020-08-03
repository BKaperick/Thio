from game import *


class TestGame(Game):
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
        self.verbose = 0
    
    def testTally(self, assertions, test_name):
        try:
            for i,result in enumerate(assertions):
                assert(result)
            self.tests_passed += 1
            return True
        except AssertionError:
            print("Failed on assertion {0} of test {1}".format(i, test_name))
            self.tests_failed += 1
            return False


    def printSummary(self):
        print("\n".join(["passed" if p else "failed" for p in self.results]))
        print("{0} / {1} tests passed ({2} failed)".format(self.tests_passed, self.tests_passed + self.tests_failed, self.tests_failed))

    def runTests(self, rerun_failed = True):
        parse_tests = (
                ('e2e4', Wh, [2,5], [4,5], False, None, True),
                ('e4',   Wh, [2,5], [4,5], False, None, True),
                ('d5',   Bl, [7,4], [5,4], False, None, False),
                ('d7d5', Bl, [7,4], [5,4], False, None, True),
                ('e4',   Wh, [2,5], [4,5], False, None, False),
                ('exd5', Wh, [4,5], [5,4], False, None, False),
                ('Pc5',  Bl, [7,3], [5,3], False, None, False),
                ('dxc6', Wh, [5,4], [6,3], True,  None, False)
                )
        for test_num,(move,team,start,end,ep_flag,prom_flag,clean_board) in enumerate(parse_tests):
            if clean_board:
                self.createCleanBoard()
            before_board = self.board.copy()
            result = self.testParseMove(move, team, [], start, end, ep_flag, prom_flag, test_num)
            if not result:
                self.verbose = 1
                print(move)
                self.board = before_board 
                print_board(self.board)
                result = self.testParseMove(move, team, [], start, end, ep_flag, prom_flag, test_num)
                print_board(self.board)
                self.verbose = 0
            self.results.append(result)
        board_tests = (
                (Wh*P, 6, 3),
                (0,    5, 3),
                (0,    5, 4)
                )
        for test_num,(piece, row, col) in enumerate(board_tests):
            result = self.testBoardPiece(piece, row, col, test_num)
            if not result:
                self.verbose = 1
                print_board(self.board)
                result = self.testBoardPiece(piece, row, col, test_num)
                self.verbose = 0
            self.results.append(result)

        self.printSummary()

    def testBoardPiece(self, piece, row, col, test_num):
        board_piece = on_board_wraparound(self.board, row, col)
        assertions = [piece == board_piece]
        return self.testTally(assertions, "boardtest " + str(test_num))

    
    def testParseMove(self, move, team, setup, exp_start, exp_end, exp_enpassant, exp_promotion, test_num):
        if setup: addPiecesToBoard(self, setup)
        (start,end),enpassant_flag,promotion_flag = self.parseMove(move, team)
        assertions = [start[0] == exp_start[0],
                start[1] == exp_start[1],
                end[0] == exp_end[0],
                end[1] == exp_end[1],
                enpassant_flag == exp_enpassant,
                exp_promotion == exp_promotion]
        movePiece(self.board, start,end, team, enpassant=enpassant_flag, promotion=promotion_flag)
        
        return self.testTally(assertions, "parsetest " + str(test_num))
            
    def createSpecificBoard(self,positions):
        for piece,r,c in positions:
            setCoord(self.board,r,c,piece) 


        self.board[:,0] = np.array([R,N,B,Q,K,B,N,R], dtype=np.int8)
        self.board[:,1] = np.array([P,P,P,P,P,P,P,P], dtype=np.int8)
        #self.board[:,-4] = np.array([0,P,fP,0,0,0,0,0], dtype=np.int8)
        self.board[:,-2] = Bl*np.array([P,P,P,P,P,P,P,P], dtype=np.int8)
        self.board[:,-1] = Bl*np.array([R,N,B,Q,K,B,N,R], dtype=np.int8)
