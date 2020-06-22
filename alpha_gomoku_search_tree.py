from gomoku import Gomoku, GomokuSearchTree
import numpy as np
import math
from time import time
import random

class AlphaGomokuSearchTree(GomokuSearchTree):
    def __init__(self, parent, board, from_move, next_player, gomoku_net, simulation_limit=2, exploration_constant=1):
        GomokuSearchTree.__init__(self, parent, board, from_move, next_player, simulation_limit=simulation_limit, exploration_constant=exploration_constant)
        self.board = board
        self.from_move = from_move
        self.next_player = next_player
        self.gomoku_net = gomoku_net
        self.policy = [1/(Gomoku.SIZE*Gomoku.SIZE)]*(Gomoku.SIZE*Gomoku.SIZE)
        self.reward = 0
        self.rollout()

    def search(self, step=5):
        simulation_count = 0
        #past_nodes = []
        #start_time = time()
        while simulation_count < self.simulation_limit:
            next_node = self.pick_next_node(self.exploration_constant)
            reward = next_node.rollout()
            next_node.backup(reward)
            simulation_count += 1
            #past_nodes.append(next_node)
        # self.print('')
        # code.interact(local=locals())
        # print(f"Number of sumulation: {simulation_count}")
        #print(f"thinking time: {time()-start_time}")
        return self.most_visited_child(random=step <= 6)

    def most_visited_child(self, random=False):
        if not random:
            return max(self.expanded_children.values(), key = lambda c: c.visit_count)
        distribution = self.get_probability_distribution()
        child_list = list(self.expanded_children.values())
        probability_list = np.array([c.visit_count for c in child_list])
        probability_list = probability_list / probability_list.sum()
        return np.random.choice(child_list, p=probability_list)
    
    def get_probability_distribution(self):
        distribution = np.zeros(Gomoku.SIZE*Gomoku.SIZE)
        for move in self.expanded_children:
            distribution[move] = self.expanded_children[move].visit_count/self.visit_count
        return distribution
    
    def create_from_move(self, move):
        if move in self.expanded_children:
            return self.expanded_children[move]
        new_board = self.board.clone_board()
        new_board.place_move(move, self.next_player)
        return AlphaGomokuSearchTree( self, new_board, move, Gomoku.other(self.next_player), self.gomoku_net, simulation_limit=self.simulation_limit, exploration_constant=self.exploration_constant)

    def ucb(self, n, exploration_constant):
            return n.reward/n.visit_count + exploration_constant*self.policy[n.from_move]*math.sqrt(self.visit_count)/(1+n.visit_count)        

    def pick_next_node(self, exploration_constant):
        def move_ucb(m):
            return exploration_constant*self.policy[m]*math.sqrt(self.visit_count)/1

        if self.is_terminal():
            return self

        if self.possible_move_list is None:
            self.possible_move_list = self.get_all_possible_moves()
            random.shuffle(self.possible_move_list)
            self.possible_move_list.sort(key=move_ucb)
        
        if not self.expanded_children:
                return self.expand_last_move()

        max_ucb_child = self.best_UCB_child(exploration_constant)

        if self.possible_move_list:
            max_ucb_move = self.possible_move_list[-1]
            if move_ucb(max_ucb_move) > self.ucb(max_ucb_child, exploration_constant):
                return self.expand_last_move()

        return max_ucb_child.pick_next_node(exploration_constant)

    def best_UCB_child(self, exploration_constant, random=False):
        if random:
            children_list = list(self.expanded_children.values())
            #print([ucb(c) for c in children_list])
            return np.random.choice(children_list)
        return max(self.expanded_children.values(), key= lambda c: self.ucb(c, exploration_constant))
    
    def rollout(self):        
        last_player = Gomoku.other(self.next_player)
        result = self.board.check_board()
        if result == last_player:
            return 1
        if result == self.next_player:
            return -1
        policy, reward = self.predict(self.board.board, last_player)
        self.policy = policy
        return reward[0]

    def encode_input(self, board, player):
        my_stone, your_stone = np.zeros((Gomoku.SIZE, Gomoku.SIZE)), np.zeros((Gomoku.SIZE, Gomoku.SIZE))
        
        for index, cell in enumerate(board):
            x = index%Gomoku.SIZE
            y = index//Gomoku.SIZE
            
            if cell == player:
                my_stone[y][x] = 1
                
            if cell == Gomoku.other(player):
                your_stone[y][x] = 1

        return np.stack((my_stone, your_stone), axis=-1)


    def predict(self, board, player):
        model_input = np.expand_dims(self.encode_input(board, player), axis=0)
        policy, reward = self.gomoku_net.model.predict(model_input)
        return policy[0], reward[0]