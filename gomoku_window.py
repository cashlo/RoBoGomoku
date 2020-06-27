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


class GomokuWindow:

	board_size = 600

	def __init__(self):
		self.window = Tk()
		self.window.title('GoMoKu')

		self.canvas = Canvas(self.window, width=self.board_size, height=self.board_size, bg="#FFD167")
		self.draw_board()
		self.canvas.pack()
		self.window.update()
		

	def mainloop(self):
		self.window.mainloop()

	def draw_board(self):
		row_height = self.board_size/Gomoku.SIZE
		for i in range(Gomoku.SIZE):
			self.canvas.create_line( (i+0.5)*row_height, 0, (i+0.5)*row_height, self.board_size, width=2)
			self.canvas.create_line(0, (i+0.5)*row_height, self.board_size, (i+0.5)*row_height, width=2)

	def draw_move(self, x, y, player):
		player_to_color = {
			Gomoku.BLACK: 'black',
			Gomoku.WHITE: 'white',
		}
		color = player_to_color[player]
		cell_size = self.board_size/Gomoku.SIZE
		margin = cell_size*0.05
		self.canvas.create_oval(x*cell_size+margin, y*cell_size+margin, (x+1)*cell_size-margin, (y+1)*cell_size-margin, fill=color,outline=color)
		self.window.update()

	def reset_board(self):
		self.canvas.destroy()
		self.canvas = Canvas(self.window, width=self.board_size, height=self.board_size, bg="#FFD167")
		self.draw_board()
		self.canvas.pack()
		self.window.update()