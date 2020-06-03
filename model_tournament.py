import glob
import tensorflow as tf
from gomoku import Gomoku, GomokuBoard
from alpha_go_zero_model import AlphaGoZeroModel
from alpha_gomoku_search_tree import AlphaGomokuSearchTree


def net_vs(net_0, net_1, number_of_games, simulation_limit=50):
	winner_count = [0, 0]
	for i in range(number_of_games):
		game = Gomoku()

		tree_dict = {
			Gomoku.BLACK: [0, AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, net_0, simulation_limit=simulation_limit)],
			Gomoku.WHITE: [1, AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, net_1, simulation_limit=simulation_limit)]
		}
		if i%2:
			tree_dict = {
				Gomoku.BLACK: tree_dict[Gomoku.WHITE],
				Gomoku.WHITE: tree_dict[Gomoku.BLACK]
			}
		#print(f"Black is net {tree_dict[Gomoku.BLACK][0]}")
		#print(f"White is net {tree_dict[Gomoku.WHITE][0]}")
		player = Gomoku.BLACK
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = tree_dict[player][1].search().from_move
			game.board.place_move(move, player)
			tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
			player = Gomoku.other(player)
			tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
			# game.board.print()
		result = game.board.check_board()
		if result != Gomoku.DRAW:
			winner = tree_dict[result][0]
			winner_count[winner] += 1
			print(f"Game {i+1}: {winner_count[0]}:{winner_count[1]}")
	print(f"Net 0 win rate: {winner_count[0]/number_of_games:.0%}")
	print(f"Net 1 win rate: {winner_count[1]/number_of_games:.0%}")
	return f"{winner_count[0]}:{winner_count[1]}"




model_name_list = sorted(glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*'))
model_list = [tf.keras.models.load_model(name) for name in model_name_list]

result_list = [ ['   ']*len(model_list) for _ in model_list]

for i in range(len(model_list)):
	for j in range(i+1, len(model_list)):
		net1 = AlphaGoZeroModel(input_board_size=Gomoku.SIZE)
		net1.model = model_list[i]
		
		net2 = AlphaGoZeroModel(input_board_size=Gomoku.SIZE)
		net2.model = model_list[j]

		result_list[i][j] = net_vs(net1, net2, 6, 5)

for r in result_list:
	print('|'.join(r))



