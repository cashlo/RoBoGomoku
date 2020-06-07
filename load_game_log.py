import pickle
from gomoku import Gomoku, GomokuBoard
#from alpha_go_zero_model import AlphaGoZeroModel
#import tensorflow as tf
import numpy as np
import os
import glob

def encode_input(board, player):
	my_stone, your_stone = np.zeros((Gomoku.SIZE, Gomoku.SIZE)), np.zeros((Gomoku.SIZE, Gomoku.SIZE))
	
	for index, cell in enumerate(board):
		x = index%Gomoku.SIZE
		y = index//Gomoku.SIZE
		
		if cell == player:
			my_stone[y][x] = 1
			
		if cell == Gomoku.other(player):
			your_stone[y][x] = 1

	return np.stack((my_stone, your_stone), axis=-1)

os.system("")


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
			

def grayscale_block(value, max_value):
	r = int(255*value/max_value)
	g = 0
	b = int(255*(1-value)/max_value)
	b = 0
	return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, '██')

# training_net = AlphaGoZeroModel(input_board_size=Gomoku.SIZE).init_model()
# training_net.model = tf.keras.models.load_model('model_1590842371.972762')

# board = GomokuBoard(size=Gomoku.SIZE)
# board.place_move(0, Gomoku.WHITE)
# board.place_move(5, Gomoku.WHITE)
# board.place_move(10, Gomoku.WHITE)
# model_input = np.expand_dims(encode_input(board.board, Gomoku.WHITE), axis=0)
# model_input = tf.image.rot90(model_input, k=1)
# policy, reward = training_net.model.predict(model_input)
# print(policy)
# print_probability_distribution(policy[0])
# policy = np.reshape(policy, (Gomoku.SIZE, Gomoku.SIZE))
# policy = np.rot90(policy, k=1)
# policy = np.reshape(policy, (1,Gomoku.SIZE*Gomoku.SIZE))
# print(policy)
# print_x(model_input[0])
# print(reward)
# print_probability_distribution(policy[0])
# print(f"{reward[0][0]:.2%}")


#lastest_model_file = max(glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*'))
#lastest_model = AlphaGoZeroModel(input_board_size=Gomoku.SIZE).init_model()
#lastest_model.model = tf.keras.models.load_model(lastest_model_file)

game_log = pickle.loads(open('game_log_5_7.pickle', "rb").read())
# print(len(game_log['x'])*10//12)
# for index in range(len(game_log['x'])*10//12,len(game_log['x'])):
for index in reversed(range(len(game_log['x']))):
	#input_index = int(input())
	#if input_index:
	#	index = input_index
	game_x = game_log['x'][index]
	game_y0 = game_log['y'][0]
	game_y1 = game_log['y'][1]
#	policy, reward = lastest_model.model.predict(np.expand_dims(game_x, axis=0))
	print_x(game_x)
	print_probability_distribution(game_y0[index])
#	print_probability_distribution(policy[0])

	print(f"{game_y1[index]:.2%}")
	input()
#	print(f"{reward[0][0]:.2%}")