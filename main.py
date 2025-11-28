"""
▗▄▄▄   ▄▄▄      ▄▄▄▄   ▄▄▄     ■         ■  ▗▞▀▚▖ ▄▄▄  ■      ▄ ▄▄▄▄      ▗▞▀▚▖   ▐▌█  ▐▌▄▄▄▄  ▄   ▄    ■  ▐▌    ▄▄▄  ▄▄▄▄  
▐▌  █ █   █     █   █ █   █ ▗▄▟▙▄▖    ▗▄▟▙▄▖▐▛▀▀▘▀▄▄▗▄▟▙▄▖    ▄ █   █     ▐▛▀▀▘   ▐▌▀▄▄▞▘█   █ █   █ ▗▄▟▙▄▖▐▌   █   █ █   █ 
▐▌  █ ▀▄▄▄▀     █   █ ▀▄▄▄▀   ▐▌        ▐▌  ▝▚▄▄▖▄▄▄▀ ▐▌      █ █   █     ▝▚▄▄▖▗▞▀▜▌     █▄▄▄▀  ▀▀▀█   ▐▌  ▐▛▀▚▖▀▄▄▄▀ █   █ 
▐▙▄▄▀                         ▐▌        ▐▌            ▐▌      █                ▝▚▄▟▌     █     ▄   █   ▐▌  ▐▌ ▐▌            
                              ▐▌        ▐▌            ▐▌                                 ▀      ▀▀▀    ▐▌                                                                                                      

Arch & Renderaction - Tron game on console

Ajouter 10 pts pour chaque mouvements, et 100 pts pour le vainqueur

Pour bouger, vous pouvez faire une remap de touche, par défaut : 
Z/Q/S/D et les fleches pour le deuxième joueurs
"""
"""
TODO DFT formule pour la forme des trails ^^ Mais bon pas la prio
https://www.datacamp.com/tutorial/forward-propagation-neural-networks
https://youtu.be/lpYfrshSZ4I?si=2HrP-vuHLTGbbBag On peut dire se que l'on veut, c'est les indiens qui sont les plus pédagoge et poussé?
"""

from os import system, path #Pour l'interaction ordi-utilisateur, on va souvent utiliser system pour "clear" la console
from math import exp #Preatique pour l'exp
from random import uniform, gauss, choice #Pour tout les choix aléatoire
from copy import deepcopy #Pour copier une instance, en changeant sont adresse mémoire
from time import sleep, mktime, localtime, ctime # ctime sec (timestamp) -> str #Gestion du temps
import json # Gestion fichier .json, utile pour sauvegarde, lecture

COLOR = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "orange": "\033[38;5;208m",
    "white": "\033[37m",
    "reset": "\033[0m"
}

CONFIG_SIZE: int = 27 - 5
CONFIG_FACTOR: int = 2
CONFIG_REAL_SIZE: int = CONFIG_SIZE * CONFIG_FACTOR
REMAP_AI = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)} # Voir la ligne 234-237


class SaveManager:
    def __init__(self, filename="save.json"):
        if not path.exists(filename):
            with open(filename, "w") as f:
                f.write("[]")
        with open(filename, "r") as f:
            self.json_content = f.read()
        self.json_content = json.loads(self.json_content)
            
        self.filename = filename
        
    def save(self, data):
        try:
            self.json_content.append(data)
            with open(self.filename, "w") as f:
                f.write(json.dumps(self.json_content, indent=4))
            return True
        except Exception as e:
            print(f"Aie Aie Aie, une erreur...: {e}")
            return False
    
    def load(self): return self.json_content

class Neuron:
    def __init__(self, input_size):
        # Initalisation Xavier/He https://www.geeksforgeeks.org/deep-learning/xavier-initialization/ car y a eu des pbs avec la méthode "traditonnel"
        limit = (2.0 / input_size)**2
        self.bias = uniform(-limit, limit)
        self.a = 0.0
        self.weights = [gauss(0, limit) for _ in range(input_size)]
    
    def sigmoid(self, x): # https://www.geogebra.org/calculator/hmxnq3ce
        x_clamped = max(-20, min(20, x)) # Min de x -20, max de x +20
        if x_clamped >= 0: # Verifie que la sigmoid et toujours dans le bon sens, voir geogebra
            return 1 / (1 + exp(-x_clamped)) # Formule de base de la sigmoid
        else:
            exp_x = exp(x_clamped)
            return exp_x / (1 + exp_x)
    
    def activation(self, inputs):
        weighted_sum = sum(inp * w for inp, w in zip(inputs, self.weights)) + self.bias # Application de la formule w0*x0 + w1*x1 + ... + bias
        self.a = self.sigmoid(weighted_sum)
        return self.a


class NeuralNetwork:
    def __init__(self, presistion):
        """
        :param vision_size: 8 * vision_size * (vision_size-1)
        Cela sert a visualiser les cases au alentours... 
        """
        
        self.input_size = 11
        self.width, self.depth = 11*presistion, presistion+1
        
        self.layers = [
            [Neuron(self.width) for _ in range(self.input_size)], # Dans un monde meilleur, les inputs sont juste une liste de 0 ^^ (TODO)
            [[Neuron(self.width) for _ in range(self.width)] for _ in range(self.depth)], # Ceci est la hidden layer, la partie du rainsonnement
            [Neuron(1) for _ in range(4)] # Les neurones output
        ]
        
    @staticmethod
    def normalize_input(loc_joueur, loc_ennemy, trails: list):
        """Normalise les inputs pour le réseau de neurones
        Toujours claude ! on le re-fera fait maison, avec peu etre du DFT"""
        WIDTH, HEIGHT = CONFIG_REAL_SIZE, CONFIG_SIZE  # Utilisez les constantes globales
        MAX_TRAILS = WIDTH * HEIGHT
        MAX_DIST = (WIDTH**2 + HEIGHT**2)**0.5
        
        normalize = lambda v, v_max: (v / (v_max / 2)) - 1
        
        def get_coords(pos): 
            return pos % WIDTH, pos // WIDTH
        
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
            normalize(x_j, WIDTH), normalize(y_j, HEIGHT),  # position joueur
            normalize(x_e, WIDTH), normalize(y_e, HEIGHT),  # position ennemi
            centre, volume, dist_debut,  # tout ce qui est trails
            normalize(y_j, HEIGHT),              # haut du mur
            normalize(HEIGHT - 1 - y_j, HEIGHT), # bas du mur
            normalize(x_j, WIDTH),               # gauche du mur
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
    
    def predict(self):
        """Version alternative avec enumerate"""
        output_values = [n.a for n in self.layers[2]]
        print(output_values)
        
        # Trouver l'index et la valeur max en une seule passe
        max_index = max(enumerate(output_values), key=lambda x: x[1])[0]
        return max_index

        
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
        child = deepcopy(self) # On vient s'autocopier dans uen autre variable

        for layer_i, layer in enumerate(child.layers[1]): # Hidden layer
            for n_i, n in enumerate(layer):
                #On choisi de prendre soi le biais du self, soit du deuxieme parent
                n.bias =  choice([self.layers[1][layer_i][n_i].bias,parent.layers[1][layer_i][n_i].bias]) #Selection des biais
                
                for i in range(len(n.weights)):
                    # Pareil avec les forces
                    n.weights[i] = choice([self.layers[1][layer_i][n_i].weights[i],parent.layers[1][layer_i][n_i].weights[i]]) # ici des poids
        
        for n_i, neuron in enumerate(child.layers[2]): # Output 
            neuron.bias = choice([self.layers[2][n_i].bias,parent.layers[2][n_i].bias]) # Meme logique ici
            for w_i in range(len(neuron.weights)):
                neuron.weights[w_i] = choice([self.layers[2][n_i].weights[w_i],parent.layers[2][n_i].weights[w_i]])
        
        child.mutate(0.4)
        return child

class Player:
    def __init__(self, symbol, color, x, y, board, player_name=None):
        self.symbol = symbol
        self.color = color
        self.x = x
        self.y = y
        self.previous_position = [self.get_pos()]
        self.trace = "░"
        
        self.player_name = player_name if player_name else f"Player_{color}"
        self.score = 0
        self.loser = False
        self.colapse = 0
        self.board = board
    
    def get_pos(self): return self.y * CONFIG_REAL_SIZE + self.x
    
    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        
        #Verifie Qu'il est dans la grille 1, taille min
        if 1 <= new_x < CONFIG_REAL_SIZE - 1 and 1 <= new_y < CONFIG_SIZE - 1:
            self.previous_position.append(self.get_pos())
            
            self.x = new_x
            self.y = new_y
            
            self.score += 10
            self.collapse = 0
            return True
        else:
            self.colapse += 1
            if self.colapse >= 7:
                if self.score == 0: self.loser = True
                self.board.game_over()
        return False
    
    def move_left(self): return self.move(-1, 0)
    def move_right(self): return self.move(1, 0)
    def move_up(self):  return self.move(0, -1)
    def move_down(self): return self.move(0, 1)
    
    def render(self): return f"{COLOR[self.color]}{self.symbol}{COLOR['reset']}"

class Player_AI(Player):
    def __init__(self, symbol, color, x, y, board, presistion, cross_over=None, player_name=None):
        super().__init__(symbol, color, x, y, board, player_name)
        
        
        self.board = board        
        self.brain = NeuralNetwork(presistion).crossover(cross_over) if cross_over else NeuralNetwork(presistion)
    
    def define_ennemy(self):
    
        for player in self.board.players:
            if player.color != self.color: self.ennemy = player
            
    def analyse_board(self):
        # On crée une liste des trails qui exclut la position actuelle de l'ennemi, sans toucher à la vraie liste
        trails = [pos for pos in self.ennemy.previous_position if pos != self.ennemy.get_pos()]
        return self.brain.normalize_input(loc_joueur=self.get_pos(), loc_ennemy=self.ennemy.get_pos(), trails=trails)

    def move_ai(self): 
        self.brain.forward(self.analyse_board())
        
        # On stocke le résultat
        move_index = self.brain.predict()
        direction = REMAP_AI[move_index]
        
        # On print et on bouge avec la même valeur
        # print(f"Move: {direction}") # Optionnel, pour debug
        self.move(*direction)
    
    def get_score(self): return self.score #TODO rendre ca moins degeulasse


class Board:
    def __init__(self, players=None):
        self.board = []
        self._create_board()
        # liste vide, ou non renvoie faux en bool - pytonite ^^
        self.players = players if players else []
        
        self.save_manager = SaveManager()
        
        self.GAME_OVER_SCREEN = """
  ▄████  ▄▄▄       ███▄ ▄███▓▓█████     ▒█████   ██▒   █▓▓█████  ██▀███  
 ██▒ ▀█▒▒████▄    ▓██▒▀█▀ ██▒▓█   ▀    ▒██▒  ██▒▓██░   █▒▓█   ▀ ▓██ ▒ ██▒
▒██░▄▄▄░▒██  ▀█▄  ▓██    ▓██░▒███      ▒██░  ██▒ ▓██  █▒░▒███   ▓██ ░▄█ ▒
░▓█  ██▓░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄    ▒██   ██░  ▒██ █░░▒▓█  ▄ ▒██▀▀█▄  
░▒▓███▀▒ ▓█   ▓██▒▒██▒   ░██▒░▒████▒   ░ ████▓▒░   ▒▀█░  ░▒████▒░██▓ ▒██▒
 ░▒   ▒  ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░   ░ ▒░▒░▒░    ░ ▐░  ░░ ▒░ ░░ ▒▓ ░▒▓░
  ░   ░   ▒   ▒▒ ░░  ░      ░ ░ ░  ░     ░ ▒ ▒░    ░ ░░   ░ ░  ░  ░▒ ░ ▒░
░ ░   ░   ░   ▒   ░      ░      ░      ░ ░ ░ ▒       ░░     ░     ░░   ░ 
      ░       ░  ░       ░      ░  ░       ░ ░        ░     ░  ░   ░     
                                                     ░                   """
        
    
    def _create_board(self): #fonction privée

        self.board = [("#", "white")] * CONFIG_REAL_SIZE # Bord du dessus
        self.border = [i for i in range(CONFIG_REAL_SIZE)]
        #Ligne des cotées
        for i in range(CONFIG_SIZE - 2):
            self.board.append(("#", "white"))
            self.border.append(len(self.board))
            
            self.board += [(" ", "black")] * (CONFIG_REAL_SIZE - 2)
            self.board.append(("#", "white"))
            self.border.append((CONFIG_REAL_SIZE - 2) + len(self.board))
            
        self.board += [("#", "white")] * CONFIG_REAL_SIZE #Bord du dessous
    
    def _check_collision(self):
        for player in self.players:
            previous_pos = player.previous_position[1:]
            if not previous_pos: return False #Si previous pos et vide, ca sert a rien de chercher
            if player.loser == True: return True # Au cas ou car ca sera pas pris en compte... et puis tout fasons le game over fonctionnera uniquement a la 2 eme iténaration...
            
            if (len(previous_pos) != len(set(previous_pos))) and len(previous_pos) > 3: # Verification d'auto colistion
                player.loser = True
                return True
            
            for other_player in self.players:
                if other_player != player:
                    if player.get_pos() in other_player.previous_position: # verification que on est pas dans le chemin de quelqu'un
                        return True
        return False

    def game_over(self):
        sleep(3)
        system("clear")
        
        print(f"{COLOR['white']}{self.GAME_OVER_SCREEN}{COLOR['reset']}")
        sleep(1)
        
        game_data = {}
        date = mktime(localtime())
        
        for player in self.players:
            if player.loser:
                print(f"{COLOR[player.color]}{player.player_name} LOSE! Score: {player.score}{COLOR['reset']}")
                game_data[player.player_name] = {
                    "score": player.score,
                    "result": "lose",
                    "mouvements": player.previous_position,
                    "date": date
                }
            else:
                player.score += 100
                print(f"{COLOR[player.color]}{player.player_name} WIN! Score: {player.score}{COLOR['reset']}")
                game_data[player.player_name] = {
                    "score": player.score,
                    "result": "win",
                    "mouvements": player.previous_position,
                    "date": date
                }
        
        self.save_manager.save(game_data)
        sleep(9)
        quit()

    def add_player(self, player): 
        for old_player in self.players:
            if old_player.player_name == player.player_name:
                ValueError("Les noms des joueurs doivent être différents, t'es un fou toi.")
        self.players.append(player)
    
    def show_stadium(self):
        #system("clear")
        loser_state = [player.loser for player in self.players]
        if self._check_collision() or (loser_state[0] != loser_state[1]):
            print("exec game over")
            self.game_over()
            return
        
        for case in range(len(self.board)): # pour afficher chaque case
            char, color = self.board[case]
        
            for p in self.players: #tracer les traces
                if case in [pos for pos in p.previous_position]:
                    char, color = p.trace, p.color
                    break
            
            for player in self.players: #tracer la pos actuelle
                if case == player.get_pos():
                    char, color = player.symbol, player.color
                    break
                
            if (case + 1) % CONFIG_REAL_SIZE == 0: #tracer les bord
                print(f"{COLOR[color]}{char}{COLOR['reset']}")
            else:
                print(f"{COLOR[color]}{char}{COLOR['reset']}", end="", flush=True)

class NEAT():
    def __init__(self, pop_n, gen_n, presistion, randomness=0.3, max_turns = 1000): # Les turns c'est mis au cas ou, histoire qu'il se fout pas de nous. 
        """
        Docstring for __init__
        
        :param self: Description
        :param pop: Nombre de population leur d'un génération (Nombre pair)
        :param gen: Nombre de génération (ou nombre d'itération)
        :param randomness: le nombre d'alléatoire, dans un nombre **compris entre 0 et 1** pitié aller pas a 1, ca sert plus a rien apres
        """
        assert pop_n%2 != 1, "Pop_n est impaire"
        self.pop_n, self.gen, self.random_ness, self.max_turns = pop_n, gen_n, randomness, max_turns
        
        self.board_instance = Board()
        self.init_pos = ((CONFIG_REAL_SIZE // 2, 1, "blue"), (CONFIG_REAL_SIZE // 2, CONFIG_SIZE - 2, "orange"))
        self.pop = [[Player_AI("O", "blue", self.init_pos[i%2][0], self.init_pos[i%2][1], self.board_instance, 3) for i in range(self.pop_n//2)],
                    [Player_AI("O", "orange", self.init_pos[(i%2)-1][0], self.init_pos[(i%2)-1][1], self.board_instance, 3) for i in range(self.pop_n//2)]]
        
    def play(self, match_i):
            ai_match = self.pop[0][match_i], self.pop[1][match_i]
            turns = 0
            
            for ai in ai_match: self.board_instance.add_player(ai)
            for ai in ai_match: ai.define_ennemy() 

            while (not ai_match[0].loser and not ai_match[1].loser) and self.max_turns >= turns:
                for ai in ai_match: 
                    ai.move_ai()

                self.board_instance.show_stadium()
                turns += 1
        
    def gen_play(self):
        best_mind = None
        for gen_i in range(self.gen):
            for game in range(self.pop_n // 2): self.play(game)

            every_player = self.pop[0] + self.pop[1]
            scores = [pop.score for pop in enumerate(every_player)]

            best_score = every_player.index(max(scores))
            best_player_gen = every_player[best_score]

            if not best_mind: 
                best_mind, best_player_gen = best_player_gen, [Player_AI("O", "blue", choice(self.init_pos)[0], choice(self.init_pos)[1], self.board_instance, 3) for i in range(self.pop_n//2)]

            self.pop = [[best_player_gen.brain.crossover(best_mind) for i in range(self.pop_n//2)],
                        [best_player_gen.brain.crossover(best_mind) for i in range(self.pop_n//2)]]
    
                    
        
        
AI_game = NEAT(20, 2, 3)
AI_game.gen_play()
# TODO init pos better managing in player_ai   https://claude.ai/share/c15ab649-05a6-4c4c-bcbb-d4a725c253a8

"""
player_blue = Player("O", "blue", CONFIG_REAL_SIZE // 2, 1)

board_instance = Board()
print(CONFIG_REAL_SIZE)
sleep(15)
board_instance.add_player(player_blue)

board_instance.show_stadium()

player_orange = Player_AI("O", "orange", CONFIG_REAL_SIZE // 2, CONFIG_SIZE - 2, board=board_instance)
board_instance.add_player(player_orange)

def demo():
    def test():
        player_blue.move_down()
        board_instance.show_stadium()

    def test1():
        player_orange.move_left()
        board_instance.show_stadium()
        
    for i in range(2):
        sleep(0.5)
        test()

    for i in range(6):
        sleep(0.5)
        test1()

demo()

print(player_orange.test())
"""