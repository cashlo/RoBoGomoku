import pickle
import numpy as np
from gomoku import Gomoku, GomokuBoard
import os
import random

game_log = pickle.loads(open('game_log_5_7.pickle', "rb").read())

def grayscale_block(value, max_value):
	r = int(255*value/max_value)
	g = 0
	b = int(255*(1-value)/max_value)
	b = 0
	return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, '██')

def print_x(x_input):
		board = GomokuBoard(size=Gomoku.SIZE)
		for y in range(Gomoku.SIZE):
			for x in range(Gomoku.SIZE):
				if x_input[y][x][0]:
					board.place_move(y*Gomoku.SIZE+x, Gomoku.WHITE)
				if x_input[y][x][1]:
					board.place_move(y*Gomoku.SIZE+x, Gomoku.BLACK)
		board.print()

def print_probability_distribution(distribution):
	max_value = max(distribution)

	for y in range(Gomoku.SIZE):
		row = ''
		for x in range(Gomoku.SIZE):
			row += grayscale_block(distribution[y*Gomoku.SIZE+x], max_value)
		print(row)

os.system("")

converted_game_log = {
	'x': [],
	'y': [[],[]]
}

for index in range(len(game_log['x'])):
	# print(game_log['x'][index])
	# print(game_log['y'][0][index])

	top_pad = random.randint(0, 8)
	left_pad = random.randint(0, 8)

	padded_x = np.pad(game_log['x'][index], [(top_pad,8-top_pad),(left_pad,8-left_pad),(0,0)])

	padded_y0= np.reshape(game_log['y'][0][index], (7,7))
	padded_y0 = np.pad(padded_y0, [(top_pad,8-top_pad),(left_pad,8-left_pad)])
	padded_y0= np.reshape(padded_y0, (-1,))
	
	# print_x(padded_x)
	# print_probability_distribution(padded_y0)

	converted_game_log['x'].append(padded_x)
	converted_game_log['y'][0].append(padded_y0)
	converted_game_log['y'][1].append(game_log['y'][1][index])

old_game_log = pickle.loads(open('game_log_5_15_old.pickle', "rb").read())

converted_game_log['x'].extend(old_game_log['x'])
converted_game_log['y'][0].extend(old_game_log['y'][0])
converted_game_log['y'][1].extend(old_game_log['y'][1])

f = open(f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle", "wb")
f.write(pickle.dumps(converted_game_log))
f.close()

	