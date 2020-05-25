import unittest
from gomoku import Gomoku
import code

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


	def test_draw(self):
		game = Gomoku()
		for move in range(game.board.size*game.board.size):
			game.board.place_move(move, 3)
		self.assertEqual(game.board.check_board(), Gomoku.DRAW)

	def test_black_win(self):
		game = Gomoku()
		for move in range(5):
			game.board.place_move(move, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.BLACK)

		game = Gomoku()
		game.board.place_move(8, Gomoku.WHITE)
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


		game = Gomoku()
		for move in [7+8*4,7+8*3,7+8*2,7+8,7]:
			game.board.place_move(move, Gomoku.BLACK)
		self.assertEqual(game.board.check_board(), Gomoku.BLACK)
		

	def test_basic_move(self):
		game = Gomoku()
		for i in range(4):
			game.board.place_move(i, Gomoku.BLACK)
		self.assertEqual(game.board.basic_move(Gomoku.BLACK), 4)

		game = Gomoku()
		for i in range(4):
			game.board.place_move(i, Gomoku.BLACK)
		self.assertEqual(game.board.basic_move(Gomoku.WHITE), 4)

		game = Gomoku()
		for i in range(4):
			game.board.place_move(i, Gomoku.BLACK)

		game.board.place_move(8, Gomoku.WHITE)
		self.assertEqual(game.board.basic_move(Gomoku.BLACK), 4)

		game = Gomoku()
		for i in [0,1,3,4]:
			game.board.place_move(i, Gomoku.BLACK)
		self.assertEqual(game.board.basic_move(Gomoku.WHITE), 2)

		game = Gomoku()
		for i in [0,1,3,4]:
			game.board.place_move(i, Gomoku.BLACK)
		self.assertEqual(game.board.basic_move(Gomoku.BLACK), 2)


	def test_MCTS(self):
		game = Gomoku()
		for i in range(4):
			game.board.place_move(i, Gomoku.BLACK)
		self.assertEqual(game.monte_carlo_move(Gomoku.WHITE), 4)

		game = Gomoku()
		for i in range(4):
			game.board.place_move(i, Gomoku.BLACK)
		self.assertEqual(game.monte_carlo_move(Gomoku.BLACK), 4)

		game = Gomoku()
		for i in [0,1,3,4]:
			game.board.place_move(i, Gomoku.BLACK)
		self.assertEqual(game.monte_carlo_move(Gomoku.WHITE), 2)

		game = Gomoku()
		for i in [0,1,3,4]:
			game.board.place_move(i, Gomoku.BLACK)
		self.assertEqual(game.monte_carlo_move(Gomoku.BLACK), 2)

		

