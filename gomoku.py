import random
from collections import defaultdict
import concurrent.futures

class Gomoku:

	EMPTY = 0
	BLACK = 1
	WHITE = 2

	IN_PROGRESS = 0
	DRAW = 3

	
	def __init__(self, board_size=9):
		self.board_size = board_size
		self.board = [0]*(board_size*board_size)

	def other(player):
		return 3 - player

	def monte_carlo_move(self, player):
		pass


	def basic_move(self, player):
		empty_position_list = [i for i, p in enumerate(self.board) if p == Gomoku.EMPTY]
		for move in empty_position_list:
			self.board[move] = player
			if self.check_board() == player:
				self.board[move] = 0
				return move
			self.board[move] = 0

		for move in empty_position_list:
			self.board[move] = Gomoku.other(player)
			if self.check_board() == Gomoku.other(player):
				self.board[move] = 0
				return move
			self.board[move] = 0

		return random.choice(empty_position_list)

	def check_board(self):
		empty_position_count = 0
		for y in range(self.board_size):
			for x in range(self.board_size):
				i = self.board_size*y+x
				cell = self.board[self.board_size*y+x]
				if x <= self.board_size-5:
					if all(p == Gomoku.BLACK for p in self.board[i:i+5]):
						return Gomoku.BLACK
					if all(p == Gomoku.WHITE for p in self.board[self.board_size*y+x:self.board_size*y+x+5]):
						return Gomoku.WHITE
				if y <= self.board_size-5:
					if all(p == Gomoku.BLACK for p in self.board[self.board_size*y+x:self.board_size*(y+5)+x:self.board_size]):
						return Gomoku.BLACK
					if all(p == Gomoku.WHITE for p in self.board[self.board_size*y+x:self.board_size*(y+5)+x:self.board_size]):
						return Gomoku.WHITE
				if y <= self.board_size-5 and x <= self.board_size-5:
					if all(p == Gomoku.BLACK for p in self.board[self.board_size*y+x:self.board_size*(y+5)+(x+5):self.board_size+1]):
						return Gomoku.BLACK
					if all(p == Gomoku.WHITE for p in self.board[self.board_size*y+x:self.board_size*(y+5)+(x+5):self.board_size+1]):
						return Gomoku.WHITE
				if y <= self.board_size-5 and x >= 4:
					if all(p == Gomoku.BLACK for p in self.board[self.board_size*y+x:self.board_size*(y+5)+(x-5):self.board_size-1]):
						return Gomoku.BLACK
					if all(p == Gomoku.WHITE for p in self.board[self.board_size*y+x:self.board_size*(y+5)+(x-5):self.board_size-1]):
						return Gomoku.WHITE
				if cell == 0:
					empty_position_count += 1
		if empty_position_count:
			return Gomoku.IN_PROGRESS
		else:
			return Gomoku.DRAW


		

	def print_board(self):
		for y in range(self.board_size):
			row = ''
			for x in range(self.board_size):
				cell = self.board[self.board_size*y+x]
				if cell == Gomoku.BLACK:
					row += '○'
				elif cell == Gomoku.WHITE:
					row += '●'
				elif x == 0 and y == 0:
					row += '┌ '
				elif x == 0 and y == self.board_size-1:
					row += '└ '
				elif x == self.board_size-1 and y == 0:
					row += '┐'
				elif x == self.board_size-1 and y == self.board_size-1:
					row += '┘'
				elif x == 0:
					row += '├ '
				elif y == 0:
					row += '┬ '
				elif x == self.board_size-1:
					row += '┤'
				elif y == self.board_size-1:
					row += '┴ '
				else:
					row += '┼ '
			print(row)

	def one_game(i):
		game = Gomoku()
		player = Gomoku.BLACK
		while game.check_board() == Gomoku.IN_PROGRESS:
			move = game.basic_move(player)
			game.board[move] = player
			player = Gomoku.other(player)
		print(f"Game {i}: {game.check_board()}")
		return game.check_board()

game_count = defaultdict(int)

with concurrent.futures.ThreadPoolExecutor() as executor:
	future_game_list = [executor.submit(Gomoku.one_game, i) for i in range(100)]
	for game in future_game_list:
		game_count[game.result()] += 1
print(game_count)