from alpha_go_zero_model import AlphaGoZeroModel
from gomoku import Gomoku, GomokuBoard
from alpha_gomoku_search_tree import AlphaGomokuSearchTree
from time import time
import pickle
import tensorflow as tf

def backfill_end_reward(game_log, game_steps_count, result, last_player):
	game_reward = [0]*game_steps_count
	index = game_steps_count-1
	reward = 1 if last_player == result else -1
	while index >= 0:
		game_reward[index] = reward
		reward = -reward
		index -= 1
	game_log['y'][1].extend(game_reward)
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
	game_log = pickle.loads(open('game_log_1591019011.6224732.pickle', "rb").read())
	game_count = {
		'original': 0,
		'training': 0
	}
	winner_list = []
	i = 0
	while True:		
		i += 1
		game = Gomoku()

		tree_dict = {
			Gomoku.BLACK: ['training', AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, training_net, simulation_limit=5)],
			Gomoku.WHITE: ['original', AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, original_net, simulation_limit=5)]
		}
		
		if i%2:
			tree_dict = {
				Gomoku.BLACK: tree_dict[Gomoku.WHITE],
				Gomoku.WHITE: tree_dict[Gomoku.BLACK]
			}

		print(f"Black is {tree_dict[Gomoku.BLACK][0]}")
		print(f"White is {tree_dict[Gomoku.WHITE][0]}")
		
		player = Gomoku.BLACK
		game_steps_count = 0
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = tree_dict[player][1].search().from_move
			game_log['x'].append(tree_dict[player][1].encode_input(game.board.board, player))
			game_log['y'][0].append(tree_dict[player][1].get_probability_distribution())
			game_steps_count += 1
			game.board.place_move(move, player)
			tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
			player = Gomoku.other(player)
			tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
			game.board.print()

		result = game.board.check_board()
		if result != Gomoku.DRAW:
			game_count[tree_dict[result][0]] += 1
			winner_list.append(tree_dict[result][0])
		backfill_end_reward(game_log, game_steps_count, result, Gomoku.other(player))
		print(f"Game{i}: {game.board.check_board()}")
		training_net.train_from_game_log(game_log)

		print(f"Training win rate: {game_count['training']/100:.0%}")
		print(f"Original win rate: {game_count['original']/100:.0%}")

		if i%10 == 0:
			saved_model_dir = f'model_{time()}'
			training_net.model.save(saved_model_dir)
			save_game_log(game_log)

		if len(winner_list) > 100:
			old_winner = winner_list.pop(0)
			game_count[old_winner] -= 1


		if i>100 and game_count['training']/100 > 0.7:
			print(f"Check point game {i}")
			
			saved_model_dir = f'model_checkpoint_{time()}'
			training_net.model.save(saved_model_dir)

			original_net.model = tf.keras.models.load_model(saved_model_dir)

			game_count = {
				'original': 0,
				'training': 0
			}
			winner_list = []
			i = 0


	return game_count

original_net =  AlphaGoZeroModel(input_board_size=Gomoku.SIZE).init_model()
training_net = AlphaGoZeroModel(input_board_size=Gomoku.SIZE, number_of_filters=64, number_of_residual_block=10).init_model()

original_net.model = tf.keras.models.load_model('model_1590861281.1492093')
# training_net.model = tf.keras.models.load_model('model_1590925717.777439')

# game_log = pickle.loads(open('game_log_1590851917.9035506.pickle', "rb").read())
# original_net.train_from_game_log(game_log)
# original_net.train_from_game_log(game_log)
# original_net.train_from_game_log(game_log)
# original_net.train_from_game_log(game_log)

# training_net.train_from_game_log(game_log)
# training_net.train_from_game_log(game_log)
# training_net.train_from_game_log(game_log)
# training_net.train_from_game_log(game_log)

# game = Gomoku()
self_play(original_net, training_net)