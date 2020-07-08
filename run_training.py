from alpha_go_zero_model import AlphaGoZeroModel
from gomoku import Gomoku, GomokuBoard
from alpha_gomoku_search_tree import AlphaGomokuSearchTree
from time import time
import pickle
import tensorflow as tf
import concurrent.futures
import glob
import os
import argparse
import sys
from gomoku_window import GomokuWindow

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

def save_game_log(game_log, file_name=f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle"):
    f = open(file_name, "wb")
    f.write(pickle.dumps(game_log))
    f.close()
        

def generate_data(game_log, net, number_of_games, gui, mind_window, simulation_limit=50):
	for i in range(number_of_games):
		game = Gomoku()
		search_tree = AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, net, simulation_limit=simulation_limit)
		player = Gomoku.BLACK
		game_steps_count = 0
		gui.set_status(f"Game {i+1}")
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = search_tree.search(step=game_steps_count, gui=mind_window).from_move

			game_log['x'].append(search_tree.encode_input(game.board.board, player))
			game_log['y'][0].append(search_tree.get_probability_distribution())
			
			game_steps_count += 1
			game.board.place_move(move, player)
			gui.draw_move(move%Gomoku.SIZE, move//Gomoku.SIZE, player)
			search_tree = search_tree.create_from_move(move)
			player = Gomoku.other(player)
			#game.board.print()
		print(f"Game {i+1}:")
		game.board.print()
		result = game.board.check_board()
		backfill_end_reward(game_log, game_steps_count, result, Gomoku.other(player))
		gui.reset_board()

def net_vs(net_0, net_1, number_of_games, game_log, gui, mind_window_0, mind_window_1, simulation_limit=50):
	winner_count = [0, 0]
	for i in range(number_of_games):
		gui.set_status(f"Game {i+1}    Score so far {winner_count[0]}:{winner_count[1]}")
		game = Gomoku()

		tree_dict = {
			Gomoku.BLACK: [
				0,
				AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, net_0, simulation_limit=simulation_limit),
				mind_window_0
			],
			Gomoku.WHITE: [
				1,
				AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, net_1, simulation_limit=simulation_limit),
				mind_window_1
			]
		}
		if i%2:
			tree_dict = {
				Gomoku.BLACK: tree_dict[Gomoku.WHITE],
				Gomoku.WHITE: tree_dict[Gomoku.BLACK]
			}
		#print(f"Black is net {tree_dict[Gomoku.BLACK][0]}")
		#print(f"White is net {tree_dict[Gomoku.WHITE][0]}")
		player = Gomoku.BLACK
		game_steps_count = 0
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = tree_dict[player][1].search(step=game_steps_count, gui=tree_dict[player][2]).from_move

			game_log['x'].append(tree_dict[player][1].encode_input(game.board.board, player))
			game_log['y'][0].append(tree_dict[player][1].get_probability_distribution())

			game_steps_count += 1
			game.board.place_move(move, player)
			gui.draw_move(move%Gomoku.SIZE, move//Gomoku.SIZE, player)
			tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
			player = Gomoku.other(player)
			tree_dict[player][1] = tree_dict[player][1].create_from_move(move)
			# game.board.print()
		game.board.print()
		result = game.board.check_board()
		backfill_end_reward(game_log, game_steps_count, result, Gomoku.other(player))
		gui.reset_board()
		if result != Gomoku.DRAW:
			winner = tree_dict[result][0]
			winner_count[winner] += 1
			print(f"Game {i+1}: {winner_count[0]}:{winner_count[1]}")
	print(f"Net 0 win rate: {winner_count[0]/number_of_games:.0%}")
	print(f"Net 1 win rate: {winner_count[1]/number_of_games:.0%}")
	return winner_count[1]/number_of_games

parser = argparse.ArgumentParser()
parser.add_argument("--gen-data", help="Generate new data with latest net", action="store_true")
parser.add_argument("--train-new-net", help="Train new NN", action="store_true")

args = parser.parse_args()
if args.gen_data:
	game_log = {
		'x': [],
		'y': [[],[]]
	}
	if os.path.isfile(f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle"):
		game_log = pickle.loads(open(f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle", "rb").read())

	best_net_so_far = AlphaGoZeroModel(input_board_size=Gomoku.SIZE).init_model()

	net_files = glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*')
	if net_files:
		lastest_model_file = max(net_files)
		print(f"Lastest net: {lastest_model_file}")
		best_net_so_far.model = tf.keras.models.load_model(lastest_model_file)

		gui = GomokuWindow("Current AI self-play to generate new data for training")
		mind_window = GomokuWindow("Considering move", show_title=False, line_width=4)

		while True:
			net_files = glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*')
			if lastest_model_file != max(net_files):
				lastest_model_file = max(net_files)
				gui.set_status(f"Lastest net: {lastest_model_file}")
				best_net_so_far.model = tf.keras.models.load_model(lastest_model_file)

			start_time = time()
			gui.set_status("Generating new data...")
			generate_data(game_log, best_net_so_far, 20, gui, mind_window, 500)
			save_game_log(game_log)
			gui.set_status(f"Time taken: {time()-start_time}")			

	else:
		print("Model file not found")

if args.train_new_net:
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
	

	best_net_so_far = AlphaGoZeroModel(input_board_size=Gomoku.SIZE).init_model()

	net_files = glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*')
	if net_files:
		lastest_model_file = max(net_files)
		print(f"Lastest net: {lastest_model_file}")
		best_net_so_far.model = tf.keras.models.load_model(lastest_model_file)

	gui = GomokuWindow("Newly trained AI fight current AI to become the data generating AI")
	mind_window_1 = GomokuWindow("Current AI", show_title=False, line_width=4)
	mind_window_2 = GomokuWindow("New AI", show_title=False, line_width=4)

	while True:
		game_log = pickle.loads(open(f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle", "rb").read())

		gui.set_status("Training new AI...")
		start_time = time()
		fresh_net = AlphaGoZeroModel(
			input_board_size=Gomoku.SIZE,
			number_of_filters=64,
			number_of_residual_block=20,
			value_head_hidden_layer_size=64
		).init_model()

		game_log['x'].extend( net_vs_game_log['x'] )
		game_log['y'][0].extend( net_vs_game_log['y'][0] )
		game_log['y'][1].extend( net_vs_game_log['y'][1] )

		fresh_net.train_from_game_log(game_log)
		print(f"Time taken: {time()-start_time}")

		gui.set_status("Checking new net performance...")
		start_time = time()
		fresh_net_win_rate = net_vs(best_net_so_far, fresh_net, 30, net_vs_game_log, gui, mind_window_1, mind_window_2, 500)
		save_game_log(net_vs_game_log, f"net_vs_game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle")
		if fresh_net_win_rate >= 0.65:
			gui.set_status("New net won!")
			best_net_so_far = fresh_net
			saved_model_dir = f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_{time()}'
			fresh_net.model.save(saved_model_dir)
		print(f"Time taken: {time()-start_time}")

parser.print_help()