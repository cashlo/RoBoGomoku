import random
from collections import defaultdict
import concurrent.futures
from monte_carlo_tree_search import Node
import code


class GomokuSearchTree(Node):
	def __init__(self, parent, board, from_move, next_player, simulation_limit=200, exploration_constant=0.5):
		Node.__init__(self, parent=parent, simulation_limit=simulation_limit, exploration_constant=exploration_constant)
		self.board = board
		self.from_move = from_move
		self.next_player = next_player


	def create_from_move(self, move):
		new_board = self.board.clone_board()
		new_board.place_move(move, self.next_player)
		return GomokuSearchTree( self, new_board, move, Gomoku.other(self.next_player), exploration_constant=self.exploration_constant)

	def rollout(self):
		simulation_board = self.board.clone_board()
		player = self.next_player
		while simulation_board.check_board() == Gomoku.IN_PROGRESS:
			move = simulation_board.basic_move(player)
			simulation_board.place_move(move, player)
			player = Gomoku.other(player)
		result = simulation_board.check_board()
		#print(f"self.next_player: {self.next_player}")
		#print(f"sim result: {result}")
		#simulation_board.print_board()


		last_player = Gomoku.other(self.next_player)
		if result == last_player:
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
			(main_diagonal_start, main_diagonal_end+1, self.size+1),
			(anti_diagonal_start, anti_diagonal_end+1, self.size-1),
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

	def rollback_move(self, move, last_move):
		self.board[move] = Gomoku.EMPTY
		self.last_move = last_move
		self.total_moves -= 1


	def basic_move(self, player):
		empty_position_list = [i for i, p in enumerate(self.board) if p == Gomoku.EMPTY]
		last_move = self.last_move
		for move in empty_position_list:
			self.place_move(move,player)
			if self.check_board() == player:
				self.rollback_move(move, last_move)
				return move
			self.rollback_move(move, last_move)

		for move in empty_position_list:
			self.place_move(move,Gomoku.other(player))
			if self.check_board() == Gomoku.other(player):
				self.rollback_move(move, last_move)
				return move
			self.rollback_move(move, last_move)

		if not empty_position_list:
			code.interact(local=locals())

		return random.choice(empty_position_list)


	def print(self):

		header = '  '
		for x in range(self.size):
			if x == self.last_move%self.size:
				header += '▼ '
			else:
				header += f'{x+1} '
		print(header)

		for y in range(self.size):
			row = f'{y+1} ' if self.last_move//self.size != y else '► '
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
	
	def __init__(self, size=9, exploration_constant=0.5):
		self.board = GomokuBoard(size)
		self.exploration_constant=exploration_constant
		self.search_tree = GomokuSearchTree(None, self.board, None, Gomoku.BLACK, exploration_constant=self.exploration_constant)
		


	def other(player):
		return 3 - player

	def monte_carlo_move(self, player):
		if self.board.last_move in self.search_tree.expanded_children:
			self.search_tree = self.search_tree.expanded_children[self.board.last_move]
		else:
			self.search_tree = GomokuSearchTree(None, self.board, None, player, exploration_constant=self.exploration_constant)
		move = self.search_tree.search().from_move
		#self.search_tree.print('')
		self.search_tree = self.search_tree.expanded_children[move]
		return move

	def one_game(i, size=9, exploration_constant=0.5):
		game = Gomoku(size, exploration_constant=exploration_constant)
		player = Gomoku.BLACK
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = game.board.basic_move(player)
			if player == Gomoku.WHITE:				
				move = game.monte_carlo_move(Gomoku.WHITE)
				# code.interact(local=locals())
			game.board.place_move(move, player)
			player = Gomoku.other(player)
			game.board.print()
		print(f"Game {i}: {game.board.check_board()}")
		return game.board.check_board()

	def human_play(size=9):
		game = Gomoku(size)
		player = Gomoku.BLACK
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = game.monte_carlo_move(player)
			if player == Gomoku.WHITE:
				game.board.print()
				x = int(input('x? '))-1
				y = int(input('y? '))-1
				move = y*game.board.size+x
				# code.interact(local=locals())
			game.board.place_move(move, player)
			player = Gomoku.other(player)
		game.board.print()
		print(f"Game: {game.board.check_board()}")

def multi_thread(number_of_games, game_size):
	game_count = defaultdict(int)

	with concurrent.futures.ThreadPoolExecutor() as executor:
		future_game_list = [executor.submit(Gomoku.one_game, i, game_size) for i in range(number_of_games)]
		for game in future_game_list:
			game_count[game.result()] += 1
	print(game_count)

def single_thread(number_of_games, game_size):
	for ec in [0.1, 1]:
		game_count = defaultdict(int)
		game_result = [Gomoku.one_game(i, size=game_size, exploration_constant=ec) for i in range(number_of_games)]
		for result in game_result:
			game_count[result] += 1
		print(f"White win rate: {game_count[2]/number_of_games:.0%} exploration_constant:{ec}")

if __name__=="__main__":
	# import timeit
	# print(timeit.timeit("single_thread(10, 5)", setup="from __main__ import single_thread", number=3))
	# print(timeit.timeit("multi_thread(10, 5)", setup="from __main__ import multi_thread", number=3))
	
	
	single_thread(30, 7)

	# Gomoku.human_play(6)
	#game = Gomoku(9)
	#for i in [0,1,3,4]:
	# 	game.board.place_move(i, Gomoku.BLACK)
	#game.board.print()
	# print(game.monte_carlo_move(Gomoku.WHITE))
	
	# code.interact(local=locals())

	#print([(n.from_move, n.reward, n.visit_count) for n in game.search_tree.expanded_children.values()])