from gomoku import Gomoku, GomokuSearchTree
import numpy as np
import math



class AlphaGomokuSearchTree(GomokuSearchTree):
    def __init__(self, parent, board, from_move, next_player, gomoku_net, simulation_limit=2, exploration_constant=1):
        GomokuSearchTree.__init__(self, parent, board, from_move, next_player, simulation_limit=simulation_limit, exploration_constant=exploration_constant)
        self.board = board
        self.from_move = from_move
        self.next_player = next_player
        self.gomoku_net = gomoku_net
        self.policy = [1/(Gomoku.SIZE*Gomoku.SIZE)]*(Gomoku.SIZE*Gomoku.SIZE)
        self.reward = 0
    
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
    
    def best_UCB_child(self, exploration_constant):
        def ucb(n):
            return n.reward/n.visit_count + exploration_constant*self.policy[n.from_move]*math.sqrt(2*math.log(self.visit_count)/n.visit_count)
        return max(self.expanded_children.values(), key=ucb)
    
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
        model_input = np.expand_dims(encode_input(board, player), axis=0)
        policy, reward = self.gomoku_net.model.predict(model_input)
        return policy[0], reward[0]