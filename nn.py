from math import log2, exp, sqrt
from random import uniform, gauss, randint
from copy import deepcopy
from time import sleep
from os import system


class Neuron:
    def __init__(self, input_size):
        # Initialisation Xavier/He https://www.geeksforgeeks.org/deep-learning/xavier-initialization/
        limit = sqrt(2.0 / input_size)
        print(input_size)
        self.bias = uniform(-limit, limit)
        self.a = 0.0
        self.weights = [gauss(0, limit) for _ in range(input_size)]
        print(self.weights)
    
    def sigmoid(self, x):
        x_clamped = max(-20, min(20, x))
        if x_clamped >= 0:
            return 1 / (1 + exp(-x_clamped))
        else:
            exp_x = exp(x_clamped)
            return exp_x / (1 + exp_x)
    
    def activation(self, inputs):
        weighted_sum = sum(inp * w for inp, w in zip(inputs, self.weights)) + self.bias
        self.a = self.sigmoid(weighted_sum)
        return self.a


class NeuralNetwork:
    def __init__(self, vision_size):
        """
        :param vision_size: 8 * vision_size * (vision_size-1)
        Cela sert a visualiser les cases au alentours... 
        """
        
        self.input_size = 4 + (8 * vision_size * (vision_size - 1)) if vision_size >= 1 else 12
        self.vision_size = vision_size
        self.depth = max(2, round(log2(max(vision_size, 2))) + 1)
        self.width = max(self.input_size + 4, 2 ** self.depth)
        
        self.layers = [
            [Neuron(self.width) for _ in range(self.input_size)],
            [[Neuron(self.width) for _ in range(self.width)] for _ in range(self.depth)],
            [Neuron(1) for _ in range(4)]
        ]
        
        self.fitness = 0
    
    def normalize_input(inputs):
        """
        :param inputs: ## Format :
        [loc joueur x, loc joueur y, loc ennemie x, loc ennemy, vision...]
        Vision :
        
        -7 trace propre
        0 vide
        7 mur
        16 ennemie
        -16 trace ennemie
        
        Pret défini sur un grille de 18x36
        """
        x = inputs[0] % 18
        y = inputs[0] // 18
        enemy_x = inputs[1] % 18
        enemy_y = inputs[1] // 18
        
        return [x / 18, y / 36, enemy_x / 18, enemy_y / 36] + [v / 16 for v in inputs[2:]]

    def forward(self, input_values):        
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
    
    def predict(self):
        return max(n.a for n in self.layers[2])
        
    

nn = NeuralNetwork(2)
print(f"Tilles des inputs {nn.input_size}")
print(nn.forward([randint(-16, 16) for _ in range(nn.input_size)]))
print(nn.predict())