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
    
    def runAllTests(self, rerun_failed=True):
        return self.runPawnTests(rerun_failed)
    def runPawnTests(self, rerun_failed = True):
        tests = (
                (self.testParseMove, 'e2e4', Wh, [], [2,5], [4,5], False, None, True),
                (self.testParseMove, 'e4',   Wh, [], [2,5], [4,5], False, None, True),
                (self.testParseMove, 'd5',   Bl, [], [7,4], [5,4], False, None, False),
                (self.testParseMove, 'd7d5', Bl, [], [7,4], [5,4], False, None, True),
                (self.testParseMove, 'e4',   Wh, [], [2,5], [4,5], False, None, False),
                (self.testParseMove, 'exd5', Wh, [], [4,5], [5,4], False, None, False),
                (self.testParseMove, 'Pc5',  Bl, [], [7,3], [5,3], False, None, False),
                (self.testParseMove, 'dxc6', Wh, [], [5,4], [6,3], True,  None, False),
                (self.testBoardPiece, Wh*P, 6, 3, False),
                (self.testBoardPiece, empty, 5, 3, False),
                (self.testBoardPiece, empty, 5, 4, False),
                (self.testParseMove, 'c7', Wh, [], [6,3], [7,3], False,  None, False),
                (self.testParseMove, 'cxb8=N', Wh, [], [7,3], [8,2], False,  None, False),
                (self.testBoardPiece, Wh*N, 8, 2, False),
                )
        return self.executeTests(tests, rerun_failed)

    def executeTests(self, tests, rerun_failed = True):
        for test_num,test in enumerate(tests):
            testFunc = test[0]
            clean_board = test[-1]
            if clean_board:
                self.createCleanBoard()
            before_board = self.board.copy()
            result = testFunc(*test[1:-1], test_num)
            if not result:
                print(test[1])
                # re-run test with verbosity set to 1
                self.verbose = 1
                self.board = before_board 
                print_board(self.board)
                result = testFunc(*test[1:-1], test_num)
                print_board(self.board)
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
