import glob
import tensorflow as tf
from gomoku import Gomoku, GomokuBoard
from alpha_go_zero_model import AlphaGoZeroModel
from alpha_gomoku_search_tree import AlphaGomokuSearchTree


def exploration_constant_vs(net, number_of_games, exploration_constant_0, exploration_constant_1, simulation_limit=50):
	winner_count = [0, 0]
	for i in range(number_of_games):
		game = Gomoku()

		tree_dict = {
			Gomoku.BLACK: [0, AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, net, simulation_limit=simulation_limit, exploration_constant=exploration_constant_0)],
			Gomoku.WHITE: [1, AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, net, simulation_limit=simulation_limit, exploration_constant=exploration_constant_1)]
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
			game.board.print()
		result = game.board.check_board()
		if result != Gomoku.DRAW:
			winner = tree_dict[result][0]
			winner_count[winner] += 1
			print(f"Game {i+1}: {winner_count[0]}:{winner_count[1]}")
	print(f"EC {exploration_constant_0} win rate: {winner_count[0]/number_of_games:.0%}")
	print(f"EC {exploration_constant_1} win rate: {winner_count[1]/number_of_games:.0%}")
	return f"{winner_count[0]}:{winner_count[1]}"




latest_net_file = max(glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*'))
net = AlphaGoZeroModel()
net.model = tf.keras.models.load_model(latest_net_file)

exploration_constant_list = [0.1, 0.5, 1, 2, 4]

result_list = [ ['   ']*len(exploration_constant_list) for _ in exploration_constant_list]


for i in range(len(exploration_constant_list)):
	for j in range(i+1, len(exploration_constant_list)):
		ec0 = exploration_constant_list[i]
		ec1 = exploration_constant_list[j]

		print(f"EC {i} vs EC {j}")
		result_list[i][j] = exploration_constant_vs(net, 6, ec0, ec1, simulation_limit=50)

for r in result_list:
	print('|'.join(r))



