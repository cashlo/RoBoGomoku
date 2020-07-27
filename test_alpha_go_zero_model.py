import unittest

import numpy as np
from alpha_go_zero_model import AlphaGoZeroModel, rotate_data

test_input_x = np.array([
	[
		[[1,11],[2,12],[3,13]],
		[[4,14],[5,15],[6,16]],
		[[7,17],[8,18],[9,19]],
	]
])

test_input_x_r1 = np.array([
	[
		[[3,13],[6,16],[9,19]],
		[[2,12],[5,15],[8,18]],
		[[1,11],[4,14],[7,17]],
	]
])

test_input_y = np.array([
	[1,2,3,4,5,6,7,8,9],
	[1,2,3,4,5,6,7,8,9],
])
test_input_y_r1 = np.array([
	[3,6,9,2,5,8,1,4,7],
	[3,6,9,2,5,8,1,4,7],
])

test_input_y1 = np.array([-1, 1])
test_input_y1_r1 = np.array([-1, 1])


class TestAlphaGoZeroModel(unittest.TestCase):


	def test_rotate_data(self):
		xo, y0o, y1o = rotate_data((test_input_x, test_input_y, test_input_y1), 3, 1)
		self.assertTrue(np.array_equal(xo.numpy(), test_input_x_r1))
		self.assertTrue(np.array_equal(y0o, test_input_y_r1))
		self.assertTrue(np.array_equal(y1o, test_input_y1_r1))

		xo, y0o, y1o = rotate_data((test_input_x_r1, test_input_y_r1, test_input_y1_r1), 3, 3)
		self.assertTrue(np.array_equal(xo.numpy(), test_input_x))
		self.assertTrue(np.array_equal(y0o, test_input_y))
		self.assertTrue(np.array_equal(y1o, test_input_y1))


		