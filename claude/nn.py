from math import log2, exp
from random import uniform

class NeuralNetwork:
    def __init__(self, input_size, learning_rate=0.1):
        self.depth = round(log2(input_size))
        self.width = 2 ** self.depth
        self.learning_rate = learning_rate
        self.layers = []
        
        # Couche input
        W = [[uniform(-1, 1) for _ in range(self.width)] for _ in range(input_size)]
        b = [[uniform(-1, 1) for _ in range(self.width)]]
        self.layers.append((W, b))
        
        # Couche caché du nn
        for _ in range(self.depth - 1):
            W = [[uniform(-1, 1) for _ in range(self.width)] for _ in range(self.width)]
            b = [[uniform(-1, 1) for _ in range(self.width)]]
            self.layers.append((W, b))
        
        # Couche output
        W = [[uniform(-1, 1)] for _ in range(self.width)]
        b = [[uniform(-1, 1)]]
        self.layers.append((W, b))
    
    def sigmoid(self, x):
        return 1 / (1 + exp(-max(-500, min(500, x))))
    
    def derive_sigmoid(self, x):
        s = self.sigmoid(x)
        return s * (1 - s)
    
    def mul_tableau(self, A, B):
        result = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]
        for i in range(len(A)):
            for j in range(len(B[0])):
                for k in range(len(B)):
                    result[i][j] += A[i][k] * B[k][j]
        return result
    
    def ajout_biais(self, A, b):
        result = [[A[i][j] + b[0][j] for j in range(len(A[0]))] for i in range(len(A))]
        return result
    
    def forward(self, X):
        self.activations = [X]
        current = X
        
        for W, b in self.layers:
            z = self.mul_tableau(current, W)
            z = self.ajout_biais(z, b)
            current = [[self.sigmoid(z[i][j]) for j in range(len(z[0]))] for i in range(len(z))]
            self.activations.append(current)
        
        return current
    
    def transpose(self, tab):
        return [[tab[j][i] for j in range(len(tab))] for i in range(len(tab[0]))]
    
    def backward(self, y):
        m = len(y)
        
        output = self.activations[-1]
        delta = [[output[i][j] - y[i][j] for j in range(len(y[0]))] for i in range(len(y))]
        
        for i in range(len(self.layers) - 1, -1, -1):
            
            W, b = self.layers[i]
            activation = self.activations[i]
            
            activation_T = self.transpose(activation)
            dW = self.mul_tableau(activation_T, delta)
            
            for j in range(len(W)):
                for k in range(len(W[0])):
                    W[j][k] -= self.learning_rate * dW[j][k] / m
            
            for k in range(len(b[0])):
                gradient = sum(delta[row][k] for row in range(len(delta))) / m
                b[0][k] -= self.learning_rate * gradient
            
            if i > 0:
                W_T = self.transpose(W)
                delta = self.mul_tableau(delta, W_T)
                next_activation = self.activations[i]
                for row in range(len(delta)):
                    for col in range(len(delta[0])):
                        sig_val = next_activation[row][col]
                        delta[row][col] *= sig_val * (1 - sig_val)
    
    def train(self, input, output, epochs):
        for epoch in range(epochs):
            self.forward(input)
            self.backward(output)
            
            if epoch % 100 == 0:
                predictions = self.forward(input)
                loss = sum((predictions[i][0] - output[i][0]) ** 2 for i in range(len(output))) / len(output)
                print(f"epoch {epoch} \ loss {loss:.6f}")
    
    def predict(self, X):
        return self.forward(X)


if __name__ == "__main__":
    x = [[0, 0], [0, 1], [1, 0], [1, 1]]
    y = [[0], [1], [1], [0]]
    
    nn = NeuralNetwork(input_size=2, learning_rate=2)
    nn.train(x, y, epochs=100000)
    
    print("\nPrédictions:")
    for i in range(len(x)):
        pred = nn.predict([x[i]])[0][0]
        print(f"Input: {x[i]} -> Prédiction: {pred:.4f}, Attendu: {y[i][0]}")