from math import log2
from random import uniform

class NeuralNetwork:
            
    def __init__(self, vision_size):
        """
        Construction d'un nn
        
        :param vision_size: 
        Le nombre d'input et defini automatiquement par 
        Ennemi_pos, Self_pos[non inclure], liste des positions visionnner au alentours [non inclure]
        
        Ces position sont défini par : 
        8 * **vision_size** * **vision_size-1** 
        """

        self.input_size = 2 + (8 * vision_size * (vision_size - 1))
        self.vision_size = vision_size
        
        self.depth = max(2, round(log2(vision_size)))
        self.width = 2 ** self.depth
        
        self.layers = [[[uniform(-1, 1), [uniform(-1, 1) for _ in range(self.width)] * 2] for _ in range(self.input_size)]]

nn = NeuralNetwork(1)
print(nn.layers)