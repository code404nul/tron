from math import log2, exp
from random import uniform, gauss, randint
from copy import deepcopy
from time import sleep
from os import system

class Neuron:
    def __init__(self, next_layer_size):
        self.bias = uniform(-1, 1)
        self.a = uniform(-1, 1)
        self.weights = [uniform(-1, 1) for _ in range(next_layer_size)]

    def sigmoid(self, x): return 1/(1+exp(-x*1.5)) #Le 1.5 c'est la sauce du chef, c'est pour accepter -2 a 2 en input, ca fait chelou de retoucher a geogebra

    def activation(self, inputs):
        weighted_sum = 0
        for input_value, weight in zip(inputs, self.weights):
            weighted_sum += input_value * weight

        weighted_sum += self.bias
        self.a = self.sigmoid(weighted_sum)
        return self.a

class NeuralNetwork:
    def __init__(self, vision_size):
        """
        :param vision_size: 8 * vision_size * (vision_size-1)
        Cela sert a visualiser les cases au alentours... 
        """
        
        self.input_size = 2 + (8 * vision_size * (vision_size - 1)) if vision_size >= 1 else 10
        self.vision_size = vision_size
        self.depth = max(2, round(log2(max(vision_size, 2))) + 1)
        self.width = max(self.input_size + 4, 2 ** self.depth)
        
        self.layers = [
            [Neuron(self.width) for _ in range(self.input_size)],
            [[Neuron(self.width) for _ in range(self.width)] for _ in range(self.depth)],
            [Neuron(1) for _ in range(4)]
        ]
        
        self.fitness = 0
    

    def forward(self, input_values):
        """
        - 2 
        """
        
        assert len(input_values) == self.input_size, f"Il doit y a voir le meme nombre d'input que initier, c'esta dire la {self.input_size}"
        
        for neuron, value in zip(self.layers[0], input_values):
            neuron.a = value

        #la vrai prog, activation des neurones dans la hidden layer
        prev_layer = self.layers[0]
        for hidden_layer in self.layers[1]:
            for neuron in hidden_layer:
                inputs = [n.a for n in prev_layer]
                neuron.activation(inputs)
            prev_layer = hidden_layer

        # Dernière propag sur la couche final
        output_layer = self.layers[2]
        for neuron in output_layer:
            inputs = [n.a for n in prev_layer]
            neuron.activation(inputs)
            
        return [n.a for n in output_layer]
    

nn = NeuralNetwork(2)
print(nn.forward([randint(0, 5) for _ in range(18)]))