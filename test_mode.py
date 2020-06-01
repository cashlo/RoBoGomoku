from alpha_go_zero_model import AlphaGoZeroModel
from gomoku import Gomoku
import pickle
import tensorflow as tf

original_net =  AlphaGoZeroModel(input_board_size=Gomoku.SIZE, number_of_residual_block=1).init_model()
game_log = pickle.loads(open('game_log_1590851917.9035506.pickle', "rb").read())
original_net.train_from_game_log(game_log)


print("Test net")
test_net =  AlphaGoZeroModel(input_board_size=Gomoku.SIZE, number_of_filters=64, number_of_residual_block=2).init_model()
test_net.train_from_game_log(game_log)

original_net.model = tf.keras.models.clone_model(test_net.model)
original_net.train_from_game_log(game_log)