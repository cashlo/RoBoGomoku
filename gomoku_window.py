from tkinter import *
import tkinter.font as tkFont

from gomoku import Gomoku, GomokuBoard

class GomokuWindow:

	board_size = 600

	def __init__(self, title='', font_size=20, line_width=2, show_title=True):
		self.window = Tk()
		self.window.title(title)
		self.window.configure(bg="black")

		self.font_style = tkFont.Font(family="Helvetica", size=font_size)

		if show_title:
			self.title_bar = Label(self.window, text=title, bg="black", fg="white", font=self.font_style)
			self.title_bar.pack()

		self.render_counter = 0

		self.canvas = Canvas(self.window, width=self.board_size, height=self.board_size, bg="#FFD167")
		self.line_width=line_width
		self.draw_lines(line_width=self.line_width)
		self.canvas.pack()

		self.status_label = Label(self.window, text='', bg="black", fg="white", font=self.font_style)
		self.status_label.pack()

		self.window.update()
		

	def mainloop(self):
		self.window.mainloop()

	def draw_lines(self, line_width=2):
		row_height = self.board_size/Gomoku.SIZE
		for i in range(Gomoku.SIZE):
			self.canvas.create_line( (i+0.5)*row_height, 0, (i+0.5)*row_height, self.board_size, width=line_width)
			self.canvas.create_line(0, (i+0.5)*row_height, self.board_size, (i+0.5)*row_height, width=line_width)

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

	def draw_board(self, board):
		if self.render_counter == 10:
			self.render_counter = 0
			self.reset_board()
			for position, piece in enumerate(board.board):
				if piece != Gomoku.EMPTY:
					self.draw_move(position%Gomoku.SIZE, position//Gomoku.SIZE, piece)
		else:
			self.render_counter += 1

	def set_status(self, status):
		self.status_label['text'] = status
		self.window.update()

	def reset_board(self):
		self.canvas.delete("all")
		#self.canvas = Canvas(self.window, width=self.board_size, height=self.board_size, bg="#FFD167")
		self.draw_lines(line_width=self.line_width)
		self.canvas.pack()
		self.window.update()