from tkinter import *
from gomoku import Gomoku, GomokuBoard
from alpha_gomoku_search_tree import AlphaGomokuSearchTree
from alpha_go_zero_model import AlphaGoZeroModel
import tensorflow as tf
from tensorflow.compat.v2.keras.utils import multi_gpu_model
import glob
import os
from time import time
import pickle

os.system("")

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


class Gomokuwindow:

	board_size = 600

	def __init__(self):

		self.game = Gomoku()
		self.drawn_moves = set()

		self.window = Tk()
		self.window.title('GoMoKu')

		self.load_nn()

		self.canvas = Canvas(self.window, width=self.board_size, height=self.board_size, bg="#FFD167")
		self.draw_board()
		self.canvas.pack()

		self.canvas.bind('<Button-1>', self.click)

		self.player1_move()

		

	def mainloop(self):
		self.window.mainloop()

	def draw_board(self):
		row_height = self.board_size/Gomoku.SIZE
		for i in range(Gomoku.SIZE):
			self.canvas.create_line( (i+0.5)*row_height, 0, (i+0.5)*row_height, self.board_size, width=2)
			self.canvas.create_line(0, (i+0.5)*row_height, self.board_size, (i+0.5)*row_height, width=2)

	def click(self, event):
		cell_size = self.board_size/Gomoku.SIZE
		x = int(event.x//cell_size)
		y = int(event.y//cell_size)
		if (x, y) in self.drawn_moves:
			return
		self.drawn_moves.add( (x, y) )
		self.draw_move(x, y, 'white')
		self.game.board.place_move(y*Gomoku.SIZE+x, Gomoku.WHITE)
		self.search_tree = self.search_tree.create_from_move(y*Gomoku.SIZE+x)
		if self.game.board.check_board() == Gomoku.IN_PROGRESS:
			self.player1_move()

		

	def draw_move(self, x, y, color):

		cell_size = self.board_size/Gomoku.SIZE
		margin = cell_size*0.05
		self.canvas.create_oval(x*cell_size+margin, y*cell_size+margin, (x+1)*cell_size-margin, (y+1)*cell_size-margin, fill=color,outline=color)


	def player1_move(self):
		start_time = time()
		player = Gomoku.BLACK
		#move = self.game.monte_carlo_move(player)
		move = self.search_tree.search(step=30).from_move
		print("final distribution:")
		print_probability_distribution(self.search_tree.get_probability_distribution())
		print("predicted distribution:")
		print_probability_distribution(self.search_tree.policy)

		self.game.board.place_move(move, player)
		self.search_tree = self.search_tree.create_from_move(move)
		self.draw_move(move%Gomoku.SIZE, move//Gomoku.SIZE, 'black')
		self.window.update()
		print(f"thinking time: {time()-start_time}")
		if self.search_tree_2 is not None:
			self.search_tree_2 = self.search_tree_2.create_from_move(move)
		if self.game.board.check_board() == Gomoku.IN_PROGRESS:
			self.player2_move()

	def player2_move(self):
		if self.search_tree_2 is None:
			return
		start_time = time()
		player = Gomoku.WHITE
		#move = self.game.monte_carlo_move(player)
		move = self.search_tree_2.search(step=30).from_move
		print("final distribution:")
		print_probability_distribution(self.search_tree_2.get_probability_distribution())
		print("predicted distribution:")
		print_probability_distribution(self.search_tree_2.policy)

		self.game.board.place_move(move, player)
		self.search_tree_2 = self.search_tree_2.create_from_move(move)
		self.search_tree = self.search_tree.create_from_move(move)
		self.draw_move(move%Gomoku.SIZE, move//Gomoku.SIZE, 'white')
		self.window.update()
		print(f"thinking time: {time()-start_time}")
		if self.game.board.check_board() == Gomoku.IN_PROGRESS:
			self.player1_move()



	def train_new_net(self):
		game_log = {
			'x': [],
			'y': [[],[]]
		}
		net_vs_game_log = {
			'x': [],
			'y': [[],[]]
		}
		if os.path.isfile(f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle"):
			game_log = pickle.loads(open(f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle", "rb").read())
		else:
			sys.exit("Game log not found")

		if os.path.isfile(f"net_vs_game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle"):
			net_vs_game_log = pickle.loads(open(f"net_vs_game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle", "rb").read())

		game_log = pickle.loads(open(f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle", "rb").read())

		print("Training new net...")
		start_time = time()
		self.picked_net = AlphaGoZeroModel(
			input_board_size=Gomoku.SIZE,
			number_of_filters=64,
			number_of_residual_block=10,
			value_head_hidden_layer_size=64
		).init_model()

		game_log['x'].extend( net_vs_game_log['x'] )
		game_log['y'][0].extend( net_vs_game_log['y'][0] )
		game_log['y'][1].extend( net_vs_game_log['y'][1] )

		self.picked_net.train_from_game_log(game_log)
		print(f"Time taken: {time()-start_time}")

	def load_nn(self):
		net_files = glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*')
		print("Pick player 1:")
		print("-1: Train new net")
		for i, file in enumerate(net_files):
			print(f"{i}: {file}")
		file_index = int(input())
		if file_index == -1:
			self.train_new_net()
		else:
			picked_model_file = net_files[file_index]
			print(f"Picked: {picked_model_file}")
			self.picked_net = AlphaGoZeroModel(input_board_size=Gomoku.SIZE)
			self.picked_net.model = tf.keras.models.load_model(picked_model_file)
		self.search_tree = AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, self.picked_net, simulation_limit=500)

		print("Pick player 2:")
		print("-1: human")
		
		for i, file in enumerate(net_files):
			print(f"{i}: {file}")
		file_index = int(input())
		self.search_tree_2 = None
		if file_index != -1:
			picked_model_file = net_files[file_index]
			print(f"Picked: {picked_model_file}")
			self.picked_net_2 = AlphaGoZeroModel(input_board_size=Gomoku.SIZE)
			self.picked_net_2.model = tf.keras.models.load_model(picked_model_file)
			self.search_tree_2 = AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, self.picked_net_2, simulation_limit=500)




window = Gomokuwindow()
window.mainloop()





