from alpha_go_zero_model import AlphaGoZeroModel
from gomoku import Gomoku, GomokuBoard
from alpha_gomoku_search_tree import AlphaGomokuSearchTree
from time import time
import pickle
import tensorflow as tf
import concurrent.futures
import glob

net_files = glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*')
print("Pick a net:")
for i, file in enumerate(net_files):
	print(f"{i}: {file}")
file_index = int(input())
picked_model_file = net_files[file_index]
print(f"Picked: {picked_model_file}")
picked_net = AlphaGoZeroModel(input_board_size=Gomoku.SIZE).init_model()
picked_net.model = tf.keras.models.load_model(picked_model_file)


game = Gomoku()
search_tree = AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, picked_net, simulation_limit=50)
player = Gomoku.BLACK
while game.board.check_board() == Gomoku.IN_PROGRESS:
	if player == Gomoku.WHITE:
		game.board.print()
		x = int(input('x? '))-1
		y = int(input('y? '))-1
		move = y*game.board.size+x
	else:
		move = search_tree.search(step=30).from_move
	game.board.place_move(move, player)
	search_tree = search_tree.create_from_move(move)
	player = Gomoku.other(player)
game.board.print()
print(f"Game: {game.board.check_board()}")

