import random
from collections import defaultdict
import concurrent.futures
from monte_carlo_tree_search import Node
import code


class GomokuSearchTree(Node):
	def __init__(self, parent, board, from_move, next_player, simulation_limit=1, exploration_constant=1):
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
			move = simulation_board.random_move(player)
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

	def check_board(self, test=False):
		if self.last_move is None:
			return Gomoku.IN_PROGRESS
		x = self.last_move%self.size
		y = self.last_move//self.size
		cell = self.board[self.last_move]

		min_x = max(0, x-(Gomoku.LINE_LENGTH-1))
		min_y = max(0, y-(Gomoku.LINE_LENGTH-1))

		max_x = min(self.size-1, x+(Gomoku.LINE_LENGTH-1))
		max_y = min(self.size-1, y+(Gomoku.LINE_LENGTH-1))

		main_diagonal_start = self.last_move - (self.size+1)*min(y-min_y, x-min_x)
		main_diagonal_end   = self.last_move + (self.size+1)*min(max_y-y, max_x-x)

		anti_diagonal_start = self.last_move - (self.size-1)*min(y-min_y, max_x-x)
		anti_diagonal_end   = self.last_move + (self.size-1)*min(max_y-y, x-min_x)

		move_line_list = [
			(self.size*y+min_x, self.size*y+max_x+1, 1),
			(self.size*min_y+x, self.size*max_y+x+1, self.size),
			(main_diagonal_start, main_diagonal_end+1, self.size+1),
			(anti_diagonal_start, anti_diagonal_end+1, self.size-1),
		]

		if test:
			for line in move_line_list:
				for m in range(line[0],line[1],line[2]):
					self.board[m] = Gomoku.WHITE
			return 0

		for line in move_line_list:
			count = 0
			for p in self.board[line[0]:line[1]:line[2]]:
				if p == cell:
					count += 1
				else:
					count = 0
				if count == Gomoku.LINE_LENGTH:
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


	def random_move(self, player):
		empty_position_list = [i for i, p in enumerate(self.board) if p == Gomoku.EMPTY]
		last_move = self.last_move

		if not empty_position_list:
			code.interact(local=locals())

		return random.choice(empty_position_list)


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
		header = '   '
		for x in range(self.size):
			if self.last_move is not None and x == self.last_move%self.size:
				header += '▼ '
			else:
				header += f'{x+1} '
		print(header)

		for y in range(self.size):
			row_name = y+1 if self.last_move is None or self.last_move//self.size != y else ' ►'
			row = f'{row_name:2} ' 
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
	
	SIZE = 15
	LINE_LENGTH = 5
	
	def __init__(self, exploration_constant=1):
		self.board = GomokuBoard(Gomoku.SIZE)
		self.exploration_constant=exploration_constant
		# self.search_tree = GomokuSearchTree(None, self.board, None, Gomoku.BLACK, exploration_constant=self.exploration_constant)
		self.search_tree_white = GomokuSearchTree(None, self.board, None, Gomoku.WHITE, simulation_limit=4000, exploration_constant=self.exploration_constant)
		self.search_tree_black = GomokuSearchTree(None, self.board, None, Gomoku.BLACK, simulation_limit=4000, exploration_constant=self.exploration_constant)
		
	def reset(self):
		self.board = GomokuBoard(Gomoku.SIZE)
		self.game_log = {
			'x': [],
			'y': [[],[]]
		}
		
		
	def self_play(self, number_of_games):
		game_count = {
			'original': 0,
			'training': 0
		}
		for i in range(number_of_games):
			tree_dict = {
				Gomoku.BLACK: ['training', AlphaGomokuSearchTree(None, self.board.clone_board(), None, Gomoku.BLACK, self.training_net, [0]*(Gomoku.SIZE*Gomoku.SIZE), 0)],
				Gomoku.WHITE: ['original', AlphaGomokuSearchTree(None, self.board.clone_board(), None, Gomoku.WHITE, self.original_net, [0]*(Gomoku.SIZE*Gomoku.SIZE), 0)]
			}
			
			if i%2:
				tree_dict = {
					Gomoku.BLACK: ['original', AlphaGomokuSearchTree(None, self.board.clone_board(), None, Gomoku.BLACK, self.original_net, [0]*(Gomoku.SIZE*Gomoku.SIZE), 0)],
					Gomoku.WHITE: ['training', AlphaGomokuSearchTree(None, self.board.clone_board(), None, Gomoku.WHITE, self.training_net, [0]*(Gomoku.SIZE*Gomoku.SIZE), 0)]
				}
			
			player = Gomoku.BLACK
			while game.board.check_board() == Gomoku.IN_PROGRESS:
				move = tree_dict[player][1].search().from_move
				self.game_log['x'].append(self.original_net.encode_input(game.board.board, player))
				self.game_log['y'][0].append(tree_dict[player][1].get_probability_distribution())
				self.game_log['y'][1].append(0)
				game.board.place_move(move, player)
				tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
				player = Gomoku.other(player)
				tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
				game.board.print()

			result = game.board.check_board()
			if result != Gomoku.DRAW:
				game_count[tree_dict[result][0]] += 1
			self.backfill_end_reward(result, Gomoku.other(player))
			print(f"Game{i}: {game.board.check_board()}")
			training_net.train_from_game_log(self.game_log)
			self.reset()
		print(f"Training win rate: {game_count['training']/number_of_games:.0%}")
		print(f"Original win rate: {game_count['original']/number_of_games:.0%}")
		return game_count
	

	def save_game_log(self):
		f = open(f"game_log_{time()}.pickle", "wb")
		f.write(pickle.dumps(self.game_log))
		f.close()
		

	

	def other(player):
		return 3 - player

	def monte_carlo_move(self, player):
		search_tree = None
		if player == Gomoku.BLACK:
			if self.board.last_move in self.search_tree_black.expanded_children:
				self.search_tree_black = self.search_tree_black.expanded_children[self.board.last_move]
			else:
				self.search_tree_black = GomokuSearchTree(None, self.board, None, player, simulation_limit=4000, exploration_constant=self.exploration_constant)
			move = self.search_tree_black.search().from_move
			self.search_tree_black = self.search_tree_black.expanded_children[move]
			return move
		else:
			if self.board.last_move in self.search_tree_white.expanded_children:
				self.search_tree_white = self.search_tree_white.expanded_children[self.board.last_move]
			else:
				self.search_tree_white = GomokuSearchTree(None, self.board, None, player, simulation_limit=4000, exploration_constant=self.exploration_constant)
			move = self.search_tree_white.search().from_move
			self.search_tree_white = self.search_tree_white.expanded_children[move]
			return move

		#if self.board.last_move in self.search_tree.expanded_children:
		#   search_tree = self.search_tree.expanded_children[self.board.last_move]
		#else:
		#   self.search_tree = GomokuSearchTree(None, self.board, None, player, exploration_constant=self.exploration_constant)

		move = search_tree.search().from_move
		#self.search_tree.print('')
		self.search_tree = self.search_tree.expanded_children[move]
		return move

	def one_game(i, size=9, exploration_constant=0.5):
		game = Gomoku(size, exploration_constant=exploration_constant)
		player = Gomoku.BLACK
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = game.monte_carlo_move(player)
			game.board.place_move(move, player)
			player = Gomoku.other(player)
			game.board.print()
		print(f"Game {i}: {game.board.check_board()}")
		return game.board.check_board()

	def human_play():
		game = Gomoku()
		player = Gomoku.BLACK
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			
			if player == Gomoku.WHITE:
				game.board.print()
				x = int(input('x? '))-1
				y = int(input('y? '))-1
				move = y*game.board.size+x
				# code.interact(local=locals())
			else:
				move = game.monte_carlo_move(player)    
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
	for ec in [1]:
		game_count = defaultdict(int)
		game_result = [Gomoku.one_game(i, size=game_size, exploration_constant=ec) for i in range(number_of_games)]
		for result in game_result:
			game_count[result] += 1
		print(f"White win rate: {game_count[2]/number_of_games:.0%} exploration_constant:{ec}")
		print(f"Black win rate: {game_count[1]/number_of_games:.0%} exploration_constant:{ec}")
		print(f"Draw rate: {game_count[3]/number_of_games:.0%} exploration_constant:{ec}")
		

if __name__=="__main__":
	# import timeit
	# print(timeit.timeit("single_thread(10, 5)", setup="from __main__ import single_thread", number=3))
	# print(timeit.timeit("multi_thread(10, 5)", setup="from __main__ import multi_thread", number=3))
	
	
	#single_thread(30, 7)


	#game = Gomoku(20)
	#game.board.place_move(20*2+1, Gomoku.BLACK)
	#game.board.print()
	#print(game.board.check_board(True))
	#game.board.print()
	
	Gomoku.human_play(7)
	#game = Gomoku(7, exploration_constant=1)
	#for i in [7+5, 7*2+4, 7*3+3]:
	# 	game.board.place_move(i, Gomoku.WHITE)

	#game.board.print()
	#game.board.place_move(game.monte_carlo_move(Gomoku.BLACK), Gomoku.BLACK)
	#game.board.print()
	# code.interact(local=locals())

	#print([(n.from_move, n.reward, n.visit_count) for n in game.search_tree.expanded_children.values()])