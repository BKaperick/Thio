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
        # print("\n".join(["passed" if p else "failed" for p in self.results]))
        print("{0} / {1} tests passed ({2} failed)".format(self.tests_passed, self.tests_passed + self.tests_failed, self.tests_failed))
    
    def runAllTests(self, rerun_failed=True):
        tests = self.pawnTests() + self.castlingTests()
        return self.executeTests(tests, rerun_failed)
    
    def castlingTests(self):
        clearNonKingRook = [[empty,1,2],
                [empty,1,3],
                [empty,1,4],
                [empty,1,6],
                [empty,1,7],
                [empty,8,2],
                [empty,8,3],
                [empty,8,4],
                [empty,8,6],
                [empty,8,7],
                ]

        tests = (
                (self.testParseMove, 'O-o', Wh, clearNonKingRook, [1,5], [1,7], False, None, True),
                (self.testBoardPiece, empty, 1, 5, False),
                (self.testBoardPiece, Wh*R, 1, 6, False),
                (self.testBoardPiece, Wh*K, 1, 7, False),
                (self.testBoardPiece, empty, 1, 8, False),
                (self.testParseMove, 'O-OO', Wh, clearNonKingRook, [1,5], [1,3], False, None, True),
                (self.testBoardPiece, empty, 1, 5, False),
                (self.testBoardPiece, Wh*R, 1, 4, False),
                (self.testBoardPiece, Wh*K, 1, 3, False),
                (self.testBoardPiece, empty, 1, 2, False),
                (self.testBoardPiece, empty, 1, 1, False),
                (self.testParseMove, 'O-OO', Bl, clearNonKingRook, [8,5], [8,3], False, None, True),
                (self.testBoardPiece, empty, 8, 5, False),
                (self.testBoardPiece, Bl*R, 8, 4, False),
                (self.testBoardPiece, Bl*K, 8, 3, False),
                (self.testBoardPiece, empty, 8, 2, False),
                (self.testBoardPiece, empty, 8, 1, False),
                (self.testParseMove, 'O-O', Bl, clearNonKingRook, [8,5], [8,7], False, None, True),
                (self.testBoardPiece, empty, 8, 5, False),
                (self.testBoardPiece, Bl*R, 8, 6, False),
                (self.testBoardPiece, Bl*K, 8, 7, False),
                (self.testBoardPiece, empty, 8, 8, False),
                )
        return tests
    def pawnTests(self):
        tests = (
                (self.testParseMove, 'e2e4', Wh, [], [2,5], [4,5], False, None, True),
                (self.testParseMove, 'e4',   Wh, [], [2,5], [4,5], False, None, True),
                (self.testParseMove, 'd5',   Bl, [], [7,4], [5,4], False, None, False),
                (self.testParseMove, 'd7d5', Bl, [], [7,4], [5,4], False, None, True),
                (self.testParseMove, 'e4',   Wh, [], [2,5], [4,5], False, None, False),
                (self.testParseMove, 'c4',   Wh, [], [2,3], [4,3], False, None, False),
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
        return tests

    def executeTests(self, tests, rerun_failed = True):
        for test_num,test in enumerate(tests):
            testFunc = test[0]
            clean_board = test[-1]
            if clean_board:
                self.createCleanBoard()
            before_board = self.board.copy()
            result = testFunc(*test[1:-1], test_num)
            if not result:
                print(test[1:])
                # re-run test with verbosity set to 1
                self.verbose = 1
                self.board = before_board 
                result = testFunc(*test[1:-1], test_num)
                print_board(self.board, team)
                self.verbose = 0
            self.results.append(result)

        self.printSummary()

    def testBoardPiece(self, piece, row, col, test_num):
        if self.verbose:
            print_board(self.board, Wh if piece>=0 else Bl)
        board_piece = on_board_wraparound(self.board, row, col)
        assertions = [piece == board_piece]
        return self.testTally(assertions, "boardtest " + str(test_num))

    
    def testParseMove(self, move, team, setup, exp_start, exp_end, exp_enpassant, exp_promotion, test_num):
        if setup: self.addPiecesToBoard(setup)
        if self.verbose > 0:
            print_board(self.board, team)
        (start,end),enpassant_flag,promotion_flag = self.parseMove(move, team)
        if start[0] < 0: start[0] += 9
        if end[0] < 0: end[0] += 9
        if start[1] < 0: start[1] += 9
        if end[1] < 0: end[1] += 9
        assertions = [start[0] == exp_start[0],
                start[1] == exp_start[1],
                end[0] == exp_end[0],
                end[1] == exp_end[1],
                enpassant_flag == exp_enpassant,
                exp_promotion == exp_promotion]
        movePiece(self.board, start,end, team, enpassant=enpassant_flag, promotion=promotion_flag)
        
        return self.testTally(assertions, "parsetest " + str(test_num))
    
    def addPiecesToBoard(self,positions):
        for piece,r,c in positions:
            setCoord(self.board,r,c,piece) 


