"""
TODO DFT formule pour la forme des trails ^^ Mais bon pas la prio
https://www.datacamp.com/tutorial/forward-propagation-neural-networks
https://youtu.be/lpYfrshSZ4I?si=2HrP-vuHLTGbbBag On peut dire se que l'on veut, c'est les indiens qui sont les plus pédagoge et poussé?
"""
from math import log2, exp, sqrt
from random import uniform, gauss, choice
from copy import deepcopy

class Neuron:
    def __init__(self, input_size):
        # Init Xavier/He https://www.geeksforgeeks.org/deep-learning/xavier-initialization/
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
    def __init__(self, precistion):
        """
        :param vision_size: 8 * vision_size * (vision_size-1)
        Cela sert a visualiser les cases au alentours... 
        """
        
        self.input_size = 11
        self.width, self.depth = 11*precistion, precistion+1
        
        self.layers = [
            [Neuron(self.width) for _ in range(self.input_size)], # Dans un monde meilleur, les inputs sont juste une liste de 0 ^^ (TODO)
            [[Neuron(self.width) for _ in range(self.width)] for _ in range(self.depth)],
            [Neuron(1) for _ in range(4)]
        ]
        
        self.fitness = 0

    def normalize_input(loc_joueur, loc_ennemy, trails: list):

        WIDTH, HEIGHT = 36, 18
        MAX_TRAILS = 236
        MAX_DIST = (WIDTH**2 + HEIGHT**2)**0.5
        
        normalize = lambda v, v_max: (v / (v_max / 2)) - 1
        
        def get_coords(pos): return pos % WIDTH, pos // WIDTH
        
        def distance(pos1, pos2):
            x1, y1 = get_coords(pos1)
            x2, y2 = get_coords(pos2)
            return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        
        x_j, y_j = get_coords(loc_joueur)
        x_e, y_e = get_coords(loc_ennemy)

        if trails:
            centre = normalize(sum(trails) / len(trails), WIDTH * HEIGHT)
            volume = normalize(len(trails), MAX_TRAILS)
            dist_debut = normalize(distance(loc_joueur, trails[0]), MAX_DIST)
        else:
            centre = volume = dist_debut = -1.0
        
        return [
            normalize(x_j, WIDTH), normalize(y_j, HEIGHT), #position joueur
            normalize(x_e, WIDTH), normalize(y_e, HEIGHT), 
            centre, volume, dist_debut, #tout ce qui est trails
            normalize(y_j, HEIGHT),              #haut du mur
            normalize(HEIGHT - 1 - y_j, HEIGHT), #bas du mur
            normalize(x_j, WIDTH),               #gauche du mur
            normalize(WIDTH - 1 - x_j, WIDTH)    # droit du mur
            ]


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
        return self.layers[2].index(max(n.a for n in self.layers[2]))
        
    def mutate(self, mutation_rate):

        for layer in self.layers[1]: #On va venir modif que la hidden layer
            for n in layer:
                n.bias += gauss(0, mutation_rate) # Appliquer de l'aléatoire comme ca sert a proposer des nouvelles solutions 
                for i in range(len(n.weights)): # On va venir modif les poids aussi, on oublie pas le s a weights
                    n.weights[i] += gauss(0, mutation_rate) #Petit formule magique
        
        for n in self.layers[2]: # A vous les outputs !
            n.bias += gauss(0, mutation_rate)
            for i in range(len(n.weights)):
                n.weights[i] += gauss(0, mutation_rate)

    def crossover(self, parent):
        """Crossover de reproduction sexuelle... donc
        :parent 
        NN a combiner"""
        child = deepcopy(self)

        for layer_i, layer in enumerate(child.layers[1]):
            for n_i, n in enumerate(layer):
                n.bias =  choice([self.layers[1][layer_i][n_i].bias,parent.layers[1][layer_i][n_i].bias]) #Selection des biais
                
                for i in range(len(n.weights)):
                    n.weights[i] = choice([self.layers[1][layer_i][n_i].weights[i],parent.layers[1][layer_i][n_i].weights[i]]) # ici des poids
        
        # Output
        for n_i, neuron in enumerate(child.layers[2]):
            neuron.bias = choice([self.layers[2][n_i].bias,parent.layers[2][n_i].bias]) 

            for w_i in range(len(neuron.weights)):
                neuron.weights[w_i] = choice([self.layers[2][n_i].weights[w_i],parent.layers[2][n_i].weights[w_i]])
        
        return child