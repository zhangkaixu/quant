#!/usr/bin/env python2
from __future__ import print_function

from keras.models import Sequential
from keras.layers import Dense, Activation

class AE:
    def __init__(self, 
            input_dim = 240, hidden_dim = 32):
        ndim = input_dim
        idim = hidden_dim

        encoder = Sequential()
        model = Sequential()

        encoder.add(Dense(output_dim=idim, input_dim=ndim))
        encoder.add(Activation("relu"))
        
        decoder = Sequential()
        decoder.add(Dense(output_dim=ndim, input_dim=idim))
        
        model.add(encoder)
        model.add(decoder)
        model.compile(optimizer='rmsprop',
                      loss='mse',
                    metrics=['accuracy'])
        
        self.decoder = decoder
        self.model = model
        self.encoder = encoder
