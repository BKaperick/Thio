from game import *

class TestGame(Game):
    def __init__(self, verbosity=0):
        BaseGame.__init__(self, verbosity, True, None, 'test_saved.txt')
        
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
        self.next_move = None
    
    def getNextMove(self,team):
        if team == self._cpTeam:
            move = self.getNextComputerMove(team)
        else:
            move = self.parseMove(self.next_move, team)

        return move
    
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
        parsing_tests = self.pawnTests() + self.castlingTests() + self.knightTests() + self.kingTests()
        string_tests = self.boardStringTests()
        cli_tests = self.commandLineTests()
        print("{0} parsing tests".format(len(parsing_tests)))
        print("{0} memory tests".format(len(string_tests)))
        print("{0} cli tests".format(len(cli_tests)))
        tests = parsing_tests + string_tests + cli_tests
        
        return self.executeTests(tests, rerun_failed)
    
    ##############################
    ###
    ### UI/GAMEPLAY TESTS
    ###
    ##############################

    def commandLineTests(self):
        tests = (
                (self.testCommandLine, 'main.py hist 0', False),
                #(self.testCommandLine, 'main.py hist 1', False),
                )
        return tests

    ##############################
    ###
    ### MEMORY TESTS
    ###
    ##############################
    
    def boardStringTests(self):
        tests = (
                (self.testMakeMove, 'e2e4', [2,5], [4,5], False, None, True),
                (self.testBoardString, True),
                (self.testMakeMove, 'e7e5', [7,5], [5,5], False, None, False),
                (self.testBoardString, False),
                )
        return tests

    
    ##############################
    ###
    ### PARSING TESTS
    ###
    ##############################

    def kingTests(self):
        aroundKing = [[empty,1,4],
                [empty,2,4],
                [empty,2,5],
                [empty,1,6],
                [empty,2,6],
                [empty,8,4]]
        tests = (
                (self.testParseMove, 'Kd1', Wh, aroundKing, [1,5], [1,4], False, None, True),
                (self.testParseMove, 'Kd2', Wh, aroundKing, [1,5], [2,4], False, None, True),
                (self.testParseMove, 'Ke2', Wh, aroundKing, [1,5], [2,5], False, None, True),
                (self.testParseMove, 'Kf1', Wh, aroundKing, [1,5], [1,6], False, None, True),
                (self.testParseMove, 'Kf2', Wh, aroundKing, [1,5], [2,6], False, None, True),
                (self.testBoardPiece, empty, 1, 5, False),
                (self.testParseMove, 'Kd8', Bl, aroundKing, [8,5], [8,4], False, None, True),
                (self.testBoardPiece, empty, 8, 5, False))
        return tests
    def knightTests(self):
        fourKnights = [ # [4,5]
                [Wh*N,3,3],
                [Wh*N,2,4],
                [Bl*N,5,3],
                [Bl*N,6,4]]

        tests = (
                (self.testParseMove, 'Nc3', Wh, [], [1,2], [3,3], False, None, True),
                (self.testBoardPiece, empty, 1, 2, False),
                (self.testBoardPiece, Wh*N, 3, 3, False),

                (self.testParseMove, 'Nce4', Wh, fourKnights, [3,3], [4,5], False, None, True),
                (self.testParseMove, 'Nc3e4', Wh, fourKnights, [3,3], [4,5], False, None, True),
                (self.testParseMove, 'Nde4', Wh, fourKnights, [2,4], [4,5], False, None, True),
                (self.testParseMove, 'N2e4', Wh, fourKnights, [2,4], [4,5], False, None, True),
                
                (self.testParseMove, 'Nce4', Bl, fourKnights, [5,3], [4,5], False, None, True),
                (self.testParseMove, 'Nc5e4', Bl, fourKnights, [5,3], [4,5], False, None, True),
                (self.testParseMove, 'Nde4', Bl, fourKnights, [6,4], [4,5], False, None, True),
                (self.testParseMove, 'N6e4', Bl, fourKnights, [6,4], [4,5], False, None, True),
                )
        return tests

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
                self.verbose += 1
                self.board = before_board 
                result = testFunc(*test[1:-1], test_num)
                print_board(self.board)
                self.verbose -= 1
            self.results.append(result)

        self.printSummary()

    def testBoardPiece(self, piece, row, col, test_num):
        if self.verbose:
            print_board(self.board, Wh if piece>=0 else Bl)
        board_piece = on_board_wraparound(self.board, row, col)
        assertions = [piece == board_piece]
        return self.testTally(assertions, "boardtest " + str(test_num))
    
    def testBoardString(self, test_num):
        '''
        Save current `self.board` to file, then reload board from file
        '''
        old_board = self.board.copy()
        old_team = self.turn
        old_board_str = board_to_string(self.board, self.turn)
        self.saveState()
        self.loadState(self.save_file.name)
        new_board_str = board_to_string(self.board, self.turn)
        new_board,new_team = string_to_board(new_board_str)
        if self.verbose:
            print("ORIGINAL:")
            print_board(old_board, old_team)
            print("RECONSTRUCTED:")
            print_board(new_board, new_team)
        assertions = [(old_board == new_board).all(),
                old_team == new_team,
                (self.board == old_board).all(),
                self.turn == old_team
                ]
        return self.testTally(assertions, "stringtest " + str(test_num))

    def testMakeMove(self, move, exp_start, exp_end, exp_enpassant, exp_promotion, test_num):
        '''
        Make move for current player as if they were a human
        '''
        self._cpTeam = -self.turn
        old_turn = self.turn
        self.next_move = move
        self.makeMove()
        assertions = [
                old_turn == -self.turn,
                ]
        parse_assertions,_,__,___,____ = self._parseMoveAssertions(move, self.turn, [], exp_start, exp_end, exp_enpassant, exp_promotion)
        return self.testTally(assertions, "movetest " + str(test_num))
    
    def _parseMoveAssertions(self, move, team, setup, exp_start, exp_end, exp_enpassant, exp_promotion):
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
        return assertions, start, end, enpassant_flag, promotion_flag
    
    def testParseMove(self, move, team, setup, exp_start, exp_end, exp_enpassant, exp_promotion, test_num):
        if setup: self.addPiecesToBoard(setup)
        assertions, start, end, enpassant_flag, promotion_flag = self._parseMoveAssertions(move, team, setup, exp_start, exp_end, exp_enpassant, exp_promotion)
        movePiece(self.board, start,end, team, enpassant=enpassant_flag, promotion=promotion_flag)
        return self.testTally(assertions, "parsetest " + str(test_num))

    def testCommandLine(self, string, test_num):
        argv = string.split()
        from main import parse_input, execute_command
        mode, options = parse_input(argv)
        result = execute_command(mode, options)
        assertions = [result == 1]
        return self.testTally(assertions, "clitest " + str(test_num))


    
    def addPiecesToBoard(self,positions):
        for piece,r,c in positions:
            setCoord(self.board,r,c,piece) 

def run_tests(verbosity):
    game = TestGame(verbosity)
    result = game.runAllTests()
    return result

