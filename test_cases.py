import chess
import unittest

class TestMoves(unittest.TestCase):

    def test_initial_board(self):
        board = chess.Board()
        board.update_all_possible_moves()
        board.turn = not board.turn
        board.update_all_possible_moves()

        rook_moves = board.get_space(0,0).possible_moves
        knight_moves = board.get_space(0,1).possible_moves
        bishop_moves = board.get_space(0,2).possible_moves
        queen_moves = board.get_space(0,3).possible_moves
        king_moves = board.get_space(0,4).possible_moves
        black_pawn = board.get_space(1,0).possible_moves
        white_pawn = board.get_space(6,0).possible_moves
        
        self.assertEqual(rook_moves,{},"Should be empty")
        self.assertEqual(bishop_moves,{},"Should be empty")
        self.assertEqual(knight_moves,{(2,0):'-',(2,2):'-'},"Incorrect moves")
        self.assertEqual(queen_moves,{},"Should be empty")
        self.assertEqual(king_moves,{},"Should be empty")
        self.assertEqual(black_pawn,{(2,0):'-',(3,0):'-'},"Incorrect moves")
        self.assertEqual(white_pawn,{(5,0):'-',(4,0):'-'},"Incorrect moves")

    def test_moves_Kasparov_vs_Topalov(self):
        white_pieces = [chess.Queen(True,(6,1)),chess.King(True,(7,1)),chess.Rook(True,(1,1)),chess.Bishop(True,(7,5)),chess.Pawn(True,(5,5)),chess.Pawn(True,(5,6)),chess.Pawn(True,(6,7))]
        black_pieces = [chess.Queen(False,(4,2)),chess.King(False,(7,3)),chess.Rook(False,(6,3)),chess.Rook(False,(0,7)),chess.Pawn(False,(3,1)),chess.Pawn(False,(1,5)),chess.Pawn(False,(2,6)),chess.Pawn(False,(1,7))]
        board = chess.Board(white_pieces,black_pieces)
        board.update_all_possible_moves()
        board.turn = not board.turn
        board.update_all_possible_moves()
        board.turn = not board.turn
        board.update_all_possible_moves()
        
        self.assertEqual(white_pieces[0].possible_moves,{(5,0):'-',(5,1):'-',(4,1):'-',(3,1):black_pieces[4],(5,2):'-',(4,3):'-',(3,4):'-',(2,5):'-',(1,6):'-',(0,7):black_pieces[3],(6,0):'-',(6,2):'-',(6,3):black_pieces[2],(7,0):'-',(7,2):'-'},"White queen incorrect moves")
        self.assertEqual(white_pieces[1].possible_moves,{(7,0):'-'},"White king incorrect moves")
        self.assertEqual(white_pieces[2].possible_moves,{(1,2):'-',(1,3):'-',(1,4):'-',(1,5):black_pieces[5],(1,0):'-',(2,1):'-',(3,1):black_pieces[4],(0,1):'-'})
        self.assertEqual(white_pieces[3].possible_moves,{(6,4):'-',(5,3):'-',(4,2):black_pieces[0],(6,6):'-',(5,7):'-'},"White bishop incorrect moves")
        self.assertEqual(white_pieces[4].possible_moves,{(4,5):'-'},"White pawn incorrect moves")
        self.assertEqual(white_pieces[5].possible_moves,{(4,6):'-'},"White pawn incorrect moves")
        self.assertEqual(white_pieces[6].possible_moves,{(5,7):'-',(4,7):'-'},"White pawn incorrect moves")

        self.assertEqual(black_pieces[0].possible_moves,{(3,2):'-',(2,2):'-',(1,2):'-',(0,2):'-',(3,3):'-',(2,4):'-',(4,1):'-',(4,0):'-',(4,3):'-',(4,4):'-',(4,5):'-',(4,6):'-',(4,7):'-',(5,1):'-',(6,0):'-',(5,2):'-',(6,2):'-',(7,2):'-',(5,3):'-',(6,4):'-',(7,5):white_pieces[3]},"Black Queen incorrect moves")
        self.assertEqual(black_pieces[1].possible_moves,{(7,4):'-'},"Black king incorrect moves")
        self.assertEqual(black_pieces[2].possible_moves,{(6,4):'-',(6,5):'-',(6,6):'-',(6,7):white_pieces[6],(6,2):'-',(6,1):white_pieces[0],(5,3):'-',(4,3):'-',(3,3):'-',(2,3):'-',(1,3):'-',(0,3):'-'}, "Black rook incorrect moves")
        self.assertEqual(black_pieces[3].possible_moves,{(0, 6): '-', (0, 5): '-', (0, 4): '-', (0, 3): '-', (0, 2): '-', (0, 1): '-', (0, 0): '-'}, "Black rook incorrect moves")
        self.assertEqual(black_pieces[4].possible_moves,{(4, 1): '-'}, "Black pawn incorrect moves")
        self.assertEqual(black_pieces[5].possible_moves,{(2, 5): '-', (3, 5): '-'}, "Black pawn incorrect moves")
        self.assertEqual(black_pieces[6].possible_moves,{(3, 6): '-'},"Black pawn incorrect moves")
        self.assertEqual(black_pieces[7].possible_moves,{(2, 7): '-', (3, 7): '-'},"Black pawn incorrect moves")


        


if __name__ == "__main__":
    unittest.main()
