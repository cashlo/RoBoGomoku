from tkinter import *
from gomoku import Gomoku, GomokuBoard
from alpha_gomoku_search_tree import AlphaGomokuSearchTree
from alpha_go_zero_model import AlphaGoZeroModel
import tensorflow as tf
import glob


class Gomokuwindow:

	board_size = 600

	def __init__(self):

		self.game = Gomoku()
		self.drawn_moves = set()

		self.window = Tk()
		self.window.title('GoMoKu')

		self.status_label = Label(self.window, text="Testing")
		self.status_label.pack()

		self.load_nn()

		self.canvas = Canvas(self.window, width=self.board_size, height=self.board_size, bg="#FFD167")
		self.draw_board()
		self.canvas.pack()

		self.canvas.bind('<Button-1>', self.click)

		# self.ai_move()

		

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
		self.ai_move()
		self.game.board.print()

		

	def draw_move(self, x, y, color):

		cell_size = self.board_size/Gomoku.SIZE
		margin = cell_size*0.05
		self.canvas.create_oval(x*cell_size+margin, y*cell_size+margin, (x+1)*cell_size-margin, (y+1)*cell_size-margin, fill=color,outline=color)

	def ai_move(self):
		player = Gomoku.BLACK
		#move = self.game.monte_carlo_move(player)
		move = self.search_tree.search(step=30).from_move

		self.game.board.place_move(move, player)
		self.search_tree = self.search_tree.create_from_move(move)
		self.draw_move(move%Gomoku.SIZE, move//Gomoku.SIZE, 'black')

	def load_nn(self):
		net_files = glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*')
		print("Pick a net:")
		for i, file in enumerate(net_files):
			print(f"{i}: {file}")
		file_index = int(input())
		picked_model_file = net_files[file_index]
		print(f"Picked: {picked_model_file}")
		self.picked_net = AlphaGoZeroModel(input_board_size=Gomoku.SIZE)
		self.picked_net.model = tf.keras.models.load_model(picked_model_file)
		self.search_tree = AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, self.picked_net, simulation_limit=200)


window = Gomokuwindow()
window.mainloop()





