import tensorflow as tf
from gomoku import Gomoku
import glob

net_files = glob.glob(f'model_{Gomoku.LINE_LENGTH}_{Gomoku.SIZE}_*')
if net_files:
	lastest_model_file = max(net_files)
	print(f"Lastest net: {lastest_model_file}")
	converter = tf.lite.TFLiteConverter.from_saved_model(lastest_model_file)
	tflite_model = converter.convert()

	with open('model.tflite', 'wb') as f:
	    f.write(tflite_model)