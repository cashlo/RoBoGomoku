import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Activation, BatchNormalization, Dense, Flatten, Input, Reshape, Conv2D, add
from tensorflow.keras.optimizers import Adam, SGD
from tensorflow.keras.regularizers import l2

import numpy as np

def rotate_data(data, board_size, rotations):
    x, y0, y1 = data

    xr  = tf.image.rot90(x, k=rotations)
    y0r = np.reshape(y0, (-1,board_size, board_size, 1))
    y0r = tf.image.rot90(y0r, k=rotations)
    y0r = np.reshape(y0r, (-1,board_size*board_size))

    return xr, y0r, y1

class AlphaGoZeroModel:
    def __init__(
            self,
            input_board_size=7,
            number_of_filters=8,
            kernal_size=3,
            number_of_residual_block=1,
            value_head_hidden_layer_size=8,
            l2_regularization=0.0001):
        self.input_board_size = input_board_size
        self.number_of_filters = number_of_filters
        self.kernal_size = kernal_size
        self.number_of_residual_block = number_of_residual_block
        self.policy_output_size = input_board_size*input_board_size
        self.value_head_hidden_layer_size = value_head_hidden_layer_size
        self.l2_regularization = l2_regularization
        
    def convolution_block(self, input_tensor):
        x = input_tensor
        x = Conv2D(self.number_of_filters, self.kernal_size, padding='same', kernel_regularizer=l2(self.l2_regularization))(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        return x
    
    def residual_block(self, input_tensor):
        x = input_tensor
        x = self.convolution_block(x)
        x = Conv2D(self.number_of_filters, self.kernal_size, padding='same', kernel_regularizer=l2(self.l2_regularization))(x)
        x = BatchNormalization()(x)
        x = add([x, input_tensor])
        x = Activation('relu')(x)
        return x
    
    def policy_head(self, input_tensor):
        x = input_tensor
        x = Conv2D(2, 1, kernel_regularizer=l2(self.l2_regularization))(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Flatten()(x)
        x = Dense(self.policy_output_size, activation='softmax', kernel_regularizer=l2(self.l2_regularization), name='policy_head')(x)
        return x
        
    def value_head(self, input_tensor):
        x = input_tensor
        x = Conv2D(1, 1)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Flatten()(x)
        x = Dense(self.value_head_hidden_layer_size, kernel_regularizer=l2(self.l2_regularization))(x)
        x = Activation('relu')(x)
        x = Dense(1, kernel_regularizer=l2(self.l2_regularization))(x)
        x = Activation('tanh', name='value_head')(x)
        return x
        
    def init_model(self):
        input_tensor = Input((self.input_board_size, self.input_board_size, 2))
        x = input_tensor
        x = self.convolution_block(x)
        for _ in range(self.number_of_residual_block):
            x = self.residual_block(x)
        self.model = Model(inputs=input_tensor, outputs=[self.policy_head(x), self.value_head(x)])
        # self.model = multi_gpu_model(self.model, gpus=2)
#        self.model.compile(SGD(learning_rate=0.0005, momentum=0.9), ['categorical_crossentropy', 'mean_squared_error'])
        self.model.compile(Adam(lr=2e-4), ['categorical_crossentropy', 'mean_squared_error'])

        
        return self

    def evaluate_from_game_log(self, game_log):
        x = np.array(game_log['x'])
        y0 = np.array(game_log['y'][0])
        y1 = np.array(game_log['y'][1])

        return self.model.evaluate(x, [y0, y1], batch_size=256, return_dict=True) #, callbacks=[callback])

    
    def train_from_game_log(self, game_log):
        half_point = -200000 # len(game_log['x'])//2
        print(len(game_log['x'])//2)
        x = np.array(game_log['x'][half_point:])
        y0 = np.array(game_log['y'][0][half_point:])
        y1 = np.array(game_log['y'][1][half_point:])

        xr1, y0r1, y1r1 = rotate_data((x, y0, y1), self.input_board_size, 1)
        xr2, y0r2, y1r2 = rotate_data((x, y0, y1), self.input_board_size, 2)
        xr3, y0r3, y1r3 = rotate_data((x, y0, y1), self.input_board_size, 3)

        xf  = np.concatenate( (x, xr1, xr2, xr3) )
        y0f = np.concatenate( (y0, y0r1, y0r2, y0r3) )
        y1f = np.concatenate( (y1, y1r1, y1r2, y1r3) )

        def step_decay(epoch):
            return 2e-4*(0.4**(epoch+1))
        callback = tf.keras.callbacks.LearningRateScheduler(step_decay)
        self.model.fit(xf, [y0f, y1f], shuffle=True, batch_size=32, epochs=3, callbacks=[callback]) #, validation_split=0.1) #, callbacks=[callback])
