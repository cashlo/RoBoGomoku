import random
from collections import defaultdict
import concurrent.futures
from monte_carlo_tree_search import Node
import code


class GomokuSearchTree(Node):
	def __init__(self, parent, board, from_move, next_player, simulation_limit=100, exploration_constant=1):
		Node.__init__(self, parent=parent, simulation_limit=simulation_limit, exploration_constant=exploration_constant)
		self.board = board
		self.from_move = from_move
		self.next_player = next_player


	def create_from_move(self, move):
		new_board = self.board.clone_board()
		new_board.place_move(move, self.next_player)
		return GomokuSearchTree( self, new_board, move, Gomoku.other(self.next_player))

	def rollout(self):
		simulation_board = self.board.clone_board()
		player = self.next_player
		while simulation_board.check_board() == Gomoku.IN_PROGRESS:
			move = simulation_board.basic_move(player)
			simulation_board.place_move(move, player)
			player = Gomoku.other(player)
		result = simulation_board.check_board()
		if result == self.next_player:
			return 1
		if result == Gomoku.DRAW:
			return 0
		return -1


	def get_all_possible_moves(self):
		if self.is_terminal():
			return []
		return [i for i, p in enumerate(self.board.board) if p == Gomoku.EMPTY]


	def is_terminal(self):
		return self.board.check_board() != Gomoku.IN_PROGRESS

class GomokuBoard:
	def __init__(self, size=9):
		self.size = size
		self.board = [0]*(size*size)
		self.last_move = None
		self.total_moves = 0


	def clone_board(self):
		new_board = GomokuBoard(self.size)
		new_board.board = self.board.copy()
		new_board.total_moves = self.total_moves
		new_board.last_move = self.last_move
		return new_board

	def check_board(self):
		if self.last_move is None:
			return Gomoku.IN_PROGRESS
		x = self.last_move%self.size
		y = self.last_move//self.size
		cell = self.board[self.last_move]

		min_x = max(0, x-4)
		min_y = max(0, y-4)

		max_x = min(self.size, x+5)
		max_y = min(self.size, y+5)

		main_diagonal_start = self.last_move - (self.size+1)*min(y-min_y, x-min_x)
		main_diagonal_end   = self.last_move + (self.size+1)*min(max_y-y, max_x-x)

		anti_diagonal_start = self.last_move - (self.size-1)*min(y-min_y, max_x-x)
		anti_diagonal_end   = self.last_move + (self.size-1)*min(max_y-y, x-min_x)

		move_line_list = [
			(self.size*y+min_x, self.size*y+max_x, 1),
			(self.size*min_y+x, self.size*max_y+x, self.size),
			(main_diagonal_start, main_diagonal_end, self.size+1),
			(anti_diagonal_start, anti_diagonal_end, self.size-1),
		]

		for line in move_line_list:
			count = 0
			for p in self.board[line[0]:line[1]:line[2]]:
				if p == cell:
					count += 1
				else:
					count = 0
				if count == 5:
					return cell

		if self.total_moves == self.size*self.size:
			return Gomoku.DRAW
		return Gomoku.IN_PROGRESS


	def place_move(self, move, player):
		if self.board[move] != Gomoku.EMPTY:
			raise ValueError("Bad Position")
		self.board[move] = player
		self.last_move = move
		self.total_moves += 1

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


	def print_board(self):
		for y in range(self.size):
			row = ''
			for x in range(self.size):
				cell = self.board[self.size*y+x]
				if cell == Gomoku.BLACK:
					#if self.size*y+x == self.last_move:
					#	row += '◌'
					#else:
						row += '○'
				elif cell == Gomoku.WHITE:
					#if self.size*y+x == self.last_move:
					#	row += '◍'
					#else:
						row += '●'
				elif x == 0 and y == 0:
					row += '┌ '
				elif x == 0 and y == self.size-1:
					row += '└ '
				elif x == self.size-1 and y == 0:
					row += '┐'
				elif x == self.size-1 and y == self.size-1:
					row += '┘'
				elif x == 0:
					row += '├ '
				elif y == 0:
					row += '┬ '
				elif x == self.size-1:
					row += '┤'
				elif y == self.size-1:
					row += '┴ '
				else:
					row += '┼ '
			print(row)


class Gomoku:

	EMPTY = 0
	BLACK = 1
	WHITE = 2

	IN_PROGRESS = 0
	DRAW = 3
	
	def __init__(self, size=9):
		self.board = GomokuBoard(size)
		self.search_tree = GomokuSearchTree(None, self.board, None, Gomoku.BLACK)


	def other(player):
		return 3 - player

	def monte_carlo_move(self, player):
		pass

	def one_game(i, size=9):
		game = Gomoku(size)
		player = Gomoku.BLACK
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = game.board.basic_move(player)
			if player == Gomoku.WHITE:
				if game.board.last_move in game.search_tree.expanded_children:
					game.search_tree = game.search_tree.expanded_children[game.board.last_move]
				else:
					game.search_tree = GomokuSearchTree(None, game.board, None, Gomoku.WHITE)
				
				move = game.search_tree.search().from_move
				# code.interact(local=locals())
				game.search_tree = game.search_tree.expanded_children[move]
				print(f"white move {move}")
			game.board.place_move(move, player)
			player = Gomoku.other(player)
			game.board.print_board()
		#print(f"Game {i}: {game.check_board()}")
		
		return game.board.check_board()

def multi_thread():
	game_count = defaultdict(int)

	with concurrent.futures.ThreadPoolExecutor() as executor:
		future_game_list = [executor.submit(Gomoku.one_game, i) for i in range(100)]
		for game in future_game_list:
			game_count[game.result()] += 1
	print(game_count)

def single_thread():
	game_count = defaultdict(int)
	game_result = [Gomoku.one_game(i) for i in range(100)]
	for result in game_result:
		game_count[result] += 1
	print(game_count)

if __name__=="__main__":
	# import timeit
	# print(timeit.timeit("single_thread()", setup="from __main__ import single_thread", number=3))
	# print(timeit.timeit("multi_thread()", setup="from __main__ import multi_thread", number=3))
	Gomoku.one_game(1, 9)