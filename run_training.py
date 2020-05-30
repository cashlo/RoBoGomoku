from alpha_go_zero_model import AlphaGoZeroModel
from gomoku import Gomoku, GomokuBoard
from alpha_gomoku_search_tree import AlphaGomokuSearchTree
from time import time
import pickle
import tensorflow as tf

def backfill_end_reward(game_log, result, last_player):
	if result == Gomoku.DRAW:
		return
	
	index = len(game_log['y'][1])-1
	reward = 1 if last_player == result else -1
	while index >= 0:
		game_log['y'][1][index] = reward
		reward = -reward
		index -= 1
	return game_log

def save_game_log(game_log):
    f = open(f"game_log_{time()}.pickle", "wb")
    f.write(pickle.dumps(game_log))
    f.close()
        

def self_play(original_net, training_net):

	game_log = {
		'x': [],
		'y': [[],[]]
	}
	game_count = {
		'original': 0,
		'training': 0
	}
	i = 0
	while True:
		
		i += 1

		game = Gomoku()


		tree_dict = {
			Gomoku.BLACK: ['training', AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, training_net, simulation_limit=1)],
			Gomoku.WHITE: ['original', AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.WHITE, original_net, simulation_limit=1)]
		}
		
		if i%2:
			tree_dict = {
				Gomoku.BLACK: tree_dict[Gomoku.WHITE],
				Gomoku.WHITE: tree_dict[Gomoku.BLACK]
			}

		print(f"Black is {tree_dict[Gomoku.BLACK][0]}")
		print(f"White is {tree_dict[Gomoku.WHITE][0]}")
		
		player = Gomoku.BLACK
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = tree_dict[player][1].search().from_move
			game_log['x'].append(tree_dict[player][1].encode_input(game.board.board, player))
			game_log['y'][0].append(tree_dict[player][1].get_probability_distribution())
			game_log['y'][1].append(0)
			game.board.place_move(move, player)
			tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
			player = Gomoku.other(player)
			tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
			game.board.print()

		result = game.board.check_board()
		if result != Gomoku.DRAW:
			game_count[tree_dict[result][0]] += 1
		backfill_end_reward(game_log, result, Gomoku.other(player))
		print(f"Game{i}: {game.board.check_board()}")
		training_net.train_from_game_log(game_log)

		print(f"Training win rate: {game_count['training']/i:.0%}")
		print(f"Original win rate: {game_count['original']/i:.0%}")

		if i%20 == 0:
			saved_model_dir = f'model_{time()}'
			tf.saved_model.save(training_net.model, saved_model_dir)
			save_game_log(game_log)


	return game_count

original_net =  AlphaGoZeroModel(input_board_size=Gomoku.SIZE).init_model()
training_net = AlphaGoZeroModel(input_board_size=Gomoku.SIZE).init_model()

game = Gomoku()
self_play(original_net, training_net)