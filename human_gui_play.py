from tkinter import *
from gomoku import Gomoku


class Gomokuwindow:

	board_size = 600

	def __init__(self):

		self.game = Gomoku()
		self.drawn_moves = set()

		self.window = Tk()
		self.window.title('GoMoKu')

		self.status_label = Label(self.window, text="Testing")
		self.status_label.pack()


		self.canvas = Canvas(self.window, width=self.board_size, height=self.board_size, bg="#FFD167")
		self.draw_board()
		self.canvas.pack()

		self.canvas.bind('<Button-1>', self.click)

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
		self.ai_move()
		self.game.board.print()

		

	def draw_move(self, x, y, color):

		cell_size = self.board_size/Gomoku.SIZE
		margin = cell_size*0.05
		self.canvas.create_oval(x*cell_size+margin, y*cell_size+margin, (x+1)*cell_size-margin, (y+1)*cell_size-margin, fill=color,outline=color)

	def ai_move(self):
		player = Gomoku.BLACK
		move = self.game.monte_carlo_move(player)
		self.game.board.place_move(move, player)
		self.draw_move(move%Gomoku.SIZE, move//Gomoku.SIZE, 'black')


window = Gomokuwindow()
window.mainloop()





