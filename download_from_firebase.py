from gomoku import Gomoku, GomokuBoard
import numpy as np
import os
import pickle

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

os.system("")

def save_game_log(game_log, sim_limit, file_name=None):
	if not file_name:
		file_name=f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_{sim_limit}_m.pickle"
	f = open(file_name, "wb")
	f.write(pickle.dumps(game_log))
	f.close()

def grayscale_block(value, max_value):
	r = int(255*value/max_value)
	g = 0
	b = int(255*(1-value)/max_value)
	b = 0
	return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, '██')

def encode_input(board):
	return np.array(board).reshape((15,15,2))

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

cred = credentials.Certificate(r"C:\Users\Cash\Documents\ai-gomoku-41896-firebase-adminsdk-4rehl-b639cfb59e.json")
firebase_admin.initialize_app(cred, {
	'databaseURL': 'https://ai-gomoku-41896-default-rtdb.firebaseio.com',
})
 
game_log_ref = db.reference("/gameLog-15-5-1500")

game_log = game_log_ref.get()

pc_game_log = {
	'x': [],
	'y': [[],[]]
}

for id in game_log:
	print(id)
	print(len(game_log[id]['x']))

	for i in range(len(game_log[id]['x'])):
		pc_game_log['x'].append(encode_input(game_log[id]['x'][i]))
		pc_game_log['y'][0].append(np.array(game_log[id]['y0'][i]))
		pc_game_log['y'][1].append(-game_log[id]['y1'][i])


		print_x(encode_input(game_log[id]['x'][i]))
		print_probability_distribution(game_log[id]['y0'][i])
		print(-game_log[id]['y1'][i])


save_game_log(pc_game_log, 1500)