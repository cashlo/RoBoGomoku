from alpha_go_zero_model import AlphaGoZeroModel
from gomoku import Gomoku, GomokuBoard
from alpha_gomoku_search_tree import AlphaGomokuSearchTree
from time import time
import pickle
import tensorflow as tf
import concurrent.futures

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
    f = open(f"game_log_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}.pickle", "wb")
    f.write(pickle.dumps(game_log))
    f.close()
        
def one_game(tree_dict):
	
	game_log = {
		'x': [],
		'y': [[],[]]
	}
	winner = ''
	
	game = Gomoku()
	
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
		winner = tree_dict[result][0]
	backfill_end_reward(game_log, game_steps_count, result, Gomoku.other(player))

	return (game_log, winner)


def generate_data(game_log, net, number_of_games, simulation_limit=50):
	for i in range(number_of_games):
		game = Gomoku()
		search_tree = AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, net, simulation_limit=simulation_limit)
		player = Gomoku.BLACK
		game_steps_count = 0
		while game.board.check_board() == Gomoku.IN_PROGRESS:
			move = search_tree.search().from_move
			game_log['x'].append(search_tree.encode_input(game.board.board, player))
			game_log['y'][0].append(search_tree.get_probability_distribution())
			game_steps_count += 1
			game.board.place_move(move, player)
			search_tree = search_tree.create_from_move(move)
			player = Gomoku.other(player)
		print(f"Game {i}:")
		game.board.print()
		result = game.board.check_board()
		backfill_end_reward(game_log, game_steps_count, result, Gomoku.other(player))

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
			print(f"Net {winner} won")
			winner_count[winner] += 1
	print(f"Net 0 win rate: {winner_count[0]/number_of_games:.0%}")
	print(f"Net 1 win rate: {winner_count[1]/number_of_games:.0%}")
	return winner_count[1]/number_of_games


	



def self_play():
	game_log = {
		'x': [],
		'y': [[],[]]
	}
	game_log = pickle.loads(open('game_log_4_5.pickle', "rb").read())
	
	best_net_so_far =  AlphaGoZeroModel(input_board_size=Gomoku.SIZE).init_model()

	while True:
#		future_game_list = []
#		with concurrent.futures.ThreadPoolExecutor() as executor:
#		for j in range(12):
#			tree_dict = {
#				Gomoku.BLACK: ['training', AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, training_net, simulation_limit=50)],
#				Gomoku.WHITE: ['original', AlphaGomokuSearchTree(None, GomokuBoard(Gomoku.SIZE), None, Gomoku.BLACK, original_net, simulation_limit=50)]
#			}
#			if j%2:
#				tree_dict = {
#					Gomoku.BLACK: tree_dict[Gomoku.WHITE],
#					Gomoku.WHITE: tree_dict[Gomoku.BLACK]
#				}
#				future_game_list.append(executor.submit(one_game, tree_dict))

#			for game in future_game_list:
#				new_game_log, winner = game.result()
		
#				new_game_log, winner = one_game(tree_dict)

#				game_log['x'].extend(new_game_log['x'])
#				game_log['y'][0].extend(new_game_log['y'][0])
#				game_log['y'][1].extend(new_game_log['y'][1])

				# if winner:
				# 	game_count[winner] += 1
				# 	winner_list.append(winner_list)

				# if len(winner_list) > 100:
				# 	old_winner = winner_list.pop(0)
				# 	game_count[old_winner] -= 1


		start_time = time()
		print("Generating new data...")
		generate_data(game_log, best_net_so_far, 50, 20)
		save_game_log(game_log)
		print(f"Time taken: {time()-start_time}")

		print("Training new net...")
		start_time = time()
		fresh_net = AlphaGoZeroModel(input_board_size=Gomoku.SIZE, number_of_filters=64, number_of_residual_block=10).init_model()
		fresh_net.train_from_game_log(game_log)
		print(f"Time taken: {time()-start_time}")

		print("Checking new net performance...")
		start_time = time()
		fresh_net_win_rate = net_vs(best_net_so_far, fresh_net, 30, 10)
		if fresh_net_win_rate > 0.7:
			print("New net won!")
			best_net_so_far = fresh_net
			saved_model_dir = f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_{time()}'
			fresh_net.model.save(saved_model_dir)
		print(f"Time taken: {time()-start_time}")
	return game_count

self_play()