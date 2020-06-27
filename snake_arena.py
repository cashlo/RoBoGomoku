import numpy as np
import random

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


class SnakeArena:
	SIZE = (20, 30)
	NUMBER_OF_PLAYERS = 1

	def __init__(self):
		self.box_setup()
		self.random_start_position()

	def box_setup(self):
		arena = np.zeros( (SnakeArena.SIZE[0]-2,SnakeArena.SIZE[1]-2) )
		self.arena = np.pad( arena, 1, constant_values=1)

	def random_start_position(self):
		self.player_position = [()]*SnakeArena.NUMBER_OF_PLAYERS
		player_position_set = set()
		for p in range(SnakeArena.NUMBER_OF_PLAYERS):
			self.player_position[p] = (
				random.randrange(1, SnakeArena.SIZE[0]),
				random.randrange(1, SnakeArena.SIZE[1])
			)
			while self.player_position[p] in player_position_set or self.arena[self.player_position[p][0]][self.player_position[p][1]]:
				self.player_position[p] = (
					random.randrange(1, SnakeArena.SIZE[0]),
					random.randrange(1, SnakeArena.SIZE[1])
				)
		self.player_tails = self.player_position[:]

	def print(self):
		for y in range(SnakeArena.SIZE[0]):
			row = ''
			for x in range(SnakeArena.SIZE[1]):
				player = 0
				for player_index, (player_y, player_x) in enumerate(self.player_position):
					if x == player_x and y == player_y:
						player = player_index+1
				if player:
					row += str(player)*2
				elif self.arena[y][x]:
					row += '██'
				else:
					row += '  '
			print(row)

SnakeArena().print()