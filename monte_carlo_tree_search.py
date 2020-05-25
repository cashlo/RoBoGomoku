import math
import code
import random

class Node:
	def __init__(self, parent=None, simulation_limit=100, exploration_constant=1):
		self.parent=parent
		self.reward = 0
		self.visit_count = 0
		self.possible_move_list = None
		self.expanded_children = {}
		self.simulation_limit = simulation_limit
		self.exploration_constant = exploration_constant

	def search(self):
		simulation_count = 0
		#past_nodes = []
		while simulation_count < self.simulation_limit:
			next_node = self.pick_next_node(self.exploration_constant)
			reward = next_node.rollout()
			next_node.backup(reward)
			simulation_count += 1
			#past_nodes.append(next_node)
			#self.print('')
			#code.interact(local=locals())
		return self.best_UCB_child(0)

	def expand_random_move(self):
		move = self.possible_move_list.pop()


		new_child = self.create_from_move(move)
		self.expanded_children[move] = new_child
		return new_child

	def best_UCB_child(self, exploration_constant):
		def ucb(n):
			return n.reward/n.visit_count + exploration_constant*math.sqrt(2*math.log(self.visit_count)/n.visit_count)
		return max(self.expanded_children.values(), key=ucb)

	def pick_next_node(self, exploration_constant):
		if self.is_terminal():
			return self

		if self.possible_move_list is None:
			self.possible_move_list = self.get_all_possible_moves()
			random.shuffle(self.possible_move_list)

		if self.possible_move_list:
			return self.expand_random_move()

		#code.interact(local=locals())
		return self.best_UCB_child(exploration_constant).pick_next_node(exploration_constant)

	def backup(self, reward):
		self.visit_count += 1
		self.reward += reward
		if self.parent is not None:
			self.parent.backup(-reward)

	def print(self, prefix):
		print(prefix + f"visit_count: {self.visit_count} reward: {self.reward} score: {self.reward/self.visit_count}")
		for move in self.expanded_children:
			self.expanded_children[move].print(prefix + f"    {move} ")

	def create_from_move(self, move):
		pass

	def rollout(self):
		pass

	def get_all_possible_moves(self):
		pass

	def is_terminal(self):
		pass
