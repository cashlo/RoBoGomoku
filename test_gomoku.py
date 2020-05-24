import unittest
from gomoku import Gomoku

class TestGomoku(unittest.TestCase):

	def test_no_win(self):
		game = Gomoku()
		self.assertEqual(game.check_board(), Gomoku.IN_PROGRESS)
		game.board[0] = Gomoku.BLACK
		self.assertEqual(game.check_board(), Gomoku.IN_PROGRESS)
		game.board[1] = Gomoku.BLACK
		self.assertEqual(game.check_board(), Gomoku.IN_PROGRESS)
		game.board[2] = Gomoku.BLACK
		self.assertEqual(game.check_board(), Gomoku.IN_PROGRESS)
		game.board[3] = Gomoku.BLACK
		self.assertEqual(game.check_board(), Gomoku.IN_PROGRESS)

	def test_black_win(self):
		game = Gomoku()
		game.board[0:5] = [Gomoku.BLACK]*5
		self.assertEqual(game.check_board(), Gomoku.BLACK)

		game = Gomoku()
		game.board[4:9] = [Gomoku.BLACK]*5
		self.assertEqual(game.check_board(), Gomoku.BLACK)

		game = Gomoku()
		game.board[6:11] = [Gomoku.BLACK]*5
		self.assertEqual(game.check_board(), Gomoku.IN_PROGRESS)

		game = Gomoku()
		game.board[game.board_size*game.board_size-5:game.board_size*game.board_size] = [Gomoku.BLACK]*5
		self.assertEqual(game.check_board(), Gomoku.BLACK)

		game = Gomoku()
		game.board[6:6+game.board_size*5:game.board_size] = [Gomoku.BLACK]*5
		self.assertEqual(game.check_board(), Gomoku.BLACK)

		game = Gomoku()
		game.board[6:6+(game.board_size-1)*5:game.board_size-1] = [Gomoku.BLACK]*5
		game.print_board()
		self.assertEqual(game.check_board(), Gomoku.BLACK)


		game = Gomoku()
		game.board[game.board_size*(game.board_size+1)-(game.board_size+1)*5:game.board_size*game.board_size:game.board_size+1] = [Gomoku.BLACK]*5
		game.print_board()
		self.assertEqual(game.check_board(), Gomoku.BLACK)
		

