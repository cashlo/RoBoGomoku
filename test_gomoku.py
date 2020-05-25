import unittest
from gomoku import Gomoku

class TestGomoku(unittest.TestCase):

	def test_no_win(self):
		game = Gomoku()
		self.assertEqual(game.board.check_board(), Gomoku.IN_PROGRESS)
		game.board.place_move(0, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.IN_PROGRESS)
		game.board.place_move(1, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.IN_PROGRESS)
		game.board.place_move(2, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.IN_PROGRESS)
		game.board.place_move(3, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.IN_PROGRESS)

	def test_black_win(self):
		game = Gomoku()
		for move in range(5):
			game.board.place_move(move, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.BLACK)

		game = Gomoku()
		for move in range(4,9):
			game.board.place_move(move, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.BLACK)

		game = Gomoku()
		for move in range(game.board.size-3,game.board.size+3):
			game.board.place_move(move, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.IN_PROGRESS)

		game = Gomoku()
		for move in range(game.board.size*game.board.size-5,game.board.size*game.board.size):
			game.board.place_move(move, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.BLACK)

		game = Gomoku()
		for move in range(6,6+game.board.size*5,game.board.size):
			game.board.place_move(move, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.BLACK)

		game = Gomoku()
		for move in range(6,6+(game.board.size-1)*5,game.board.size-1):
			game.board.place_move(move, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.BLACK)


		game = Gomoku()
		for move in range(game.board.size*(game.board.size+1)-(game.board.size+1)*5,game.board.size*game.board.size,game.board.size+1):
			game.board.place_move(move, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.BLACK)
		

