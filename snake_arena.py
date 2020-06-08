import numpy as np
import random

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