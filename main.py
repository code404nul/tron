"""
DO NOT TEST IN EDUPYTHON NOW !!!
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

GENRATING_MSG = """
   ___                          _   _                   
  / _ \___ _ __   ___ _ __ __ _| |_(_)_ __   __ _       
 / /_\/ _ \ '_ \ / _ \ '__/ _` | __| | '_ \ / _` |      
/ /_\\  __/ | | |  __/ | | (_| | |_| | | | | (_| |_ _ _ 
\____/\___|_| |_|\___|_|  \__,_|\__|_|_| |_|\__, (_|_|_)
                                            |___/       """

CONFIG_SIZE: int = 27 - 5
CONFIG_FACTOR: int = 2
CONFIG_REAL_SIZE: int = CONFIG_SIZE * CONFIG_FACTOR
REMAP_AI = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)} # Voir la ligne 234-237

def del_recurrance(liste):
    resultat = []
    for ele in liste:
        if not resultat or ele != resultat[-1]: resultat.append(ele)
    return resultat


class SaveManager:
    def __init__(self, filename="save.json"):
        if not path.exists(filename):
            with open(filename, "w") as f:
                f.write("[]")
        with open(filename, "r") as f:
            self.json_content = f.read()
        self.json_content = json.loads(self.json_content) # Par defaut config.json doit contenir une liste video sinon erreur TODO
            
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
        self.width, self.depth = 32*max(1, presistion), presistion+1
        
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
            self.previous_position.append(self.get_pos())
            self.colapse += 1
            if self.colapse >= 7:
                self.loser = True
                self.score = 0
                #self.board.game_over()
        return False
    
    def move_from_pos(self, case):
        distance = self.get_pos() - case
        if distance == CONFIG_REAL_SIZE: self.move(0, -1)
        elif distance == -CONFIG_REAL_SIZE: self.move(0, 1)
        elif distance == 1: self.move(-1, 0)
        elif distance == -1: self.move(1, 0) # TODO corriger ca
        
    def move_left(self): return self.move(-1, 0)
    def move_right(self): return self.move(1, 0)
    def move_up(self):  return self.move(0, -1)
    def move_down(self): return self.move(0, 1)
    
    def render(self): return f"{COLOR[self.color]}{self.symbol}{COLOR['reset']}"


class Player_AI(Player):
    DEFAULT_CONFIG = {
        "blue": {
            "x": CONFIG_REAL_SIZE // 2,
            "y": 1,
            "symbol": "O"
        },
        "orange": {
            "x": CONFIG_REAL_SIZE // 2,
            "y": CONFIG_SIZE - 2,
            "symbol": "X"
        }
    }
    
    def __init__(self, color, board, presistion, cross_over=None, player_name=None):

        config = self.DEFAULT_CONFIG[color]
        super().__init__(
            symbol=config["symbol"],
            color=color,
            x=config["x"],
            y=config["y"],
            board=board, 
            player_name=player_name)
        
        self.brain = NeuralNetwork(presistion).crossover(cross_over) if cross_over else NeuralNetwork(presistion)
        self.ennemy = None
    
    def define_ennemy(self):
        for player in self.board.players:
            if player.color != self.color: 
                self.ennemy = player
            
    def analyse_board(self):
        trails = [pos for pos in self.ennemy.previous_position if pos != self.ennemy.get_pos()]
        return self.brain.normalize_input(loc_joueur=self.get_pos(), loc_ennemy=self.ennemy.get_pos(), trails=trails)

    def move_ai(self): 
        self.brain.forward(self.analyse_board())
        
        move_index = self.brain.predict()
        direction = REMAP_AI[move_index]
        
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
        sleep(0)
        system("clear")
        
        #print(f"{COLOR['white']}{self.GAME_OVER_SCREEN}{COLOR['reset']}")
        sleep(0)
        
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
        
    def add_player(self, player): 
        for old_player in self.players:
            if old_player.player_name == player.player_name:
                ValueError("Les noms des joueurs doivent être différents, t'es un fou toi.")
        self.players.append(player)
    
    def show_stadium(self, death_at_game_over=True):
        #system("clear")

        loser_state = [player.loser for player in self.players]
        if (self._check_collision() or (loser_state[0] != loser_state[1])):
            print("exec game over")
            if death_at_game_over: self.game_over()
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
    def __init__(self, pop_n, gen_n, presistion, randomness=0.3, max_turns=1000): 
        assert pop_n % 2 == 0, "Pop_n doit être pair"
        self.pop_n, self.gen, self.random_ness, self.max_turns = pop_n, gen_n, randomness, max_turns
        
        self.board_instance = Board()
        
        self.pop = [
            [Player_AI("blue", self.board_instance, presistion) for _ in range(self.pop_n // 2)],
            [Player_AI("orange", self.board_instance, presistion) for _ in range(self.pop_n // 2)]
        ]
        
    def play(self, match_i):
        ai_match = (self.pop[0][match_i], self.pop[1][match_i])
        turns = 0

        for ai in ai_match: self.board_instance.add_player(ai)
        for ai in ai_match: 
            ai.define_ennemy()
            ai.previous_position = []

        while turns < self.max_turns:
            before = [ai.loser for ai in ai_match]

            for ai in ai_match:
                ai.move_ai()
                turns += 1

            if before != [ai.loser for ai in ai_match]:
                break
        
    def rewind_game(self, gen_i):
        blue_player_pos, orange_player_pos = self.pop[0][self.best_overall_match_id].previous_position, self.pop[1][self.best_overall_match_id].previous_position
        #blue_player_pos, orange_player_pos = del_recurrance(blue_player_pos), del_recurrance(orange_player_pos)

        board_instance_a = Board()

        blue_player, orange_player = Player("O", "blue", CONFIG_REAL_SIZE // 2, 1, board_instance_a), Player("X", "orange", CONFIG_REAL_SIZE // 2, CONFIG_SIZE - 2, board_instance_a)
        
        board_instance_a.add_player(blue_player)
        board_instance_a.add_player(orange_player)

        color = "green" if gen_i/self.gen < 1 else "blue" if gen_i/self.gen < 2 else "red"

        for i in range(1, len(blue_player_pos)):
            print()
            print(GENRATING_MSG)
            print(COLOR[color] + "="*20 + str(gen_i) + "/" + str(self.gen) + "=" * 20 + COLOR["reset"] + "\n")

            blue_player.move_from_pos(blue_player_pos[i])
            orange_player.move_from_pos(orange_player_pos[i])

            board_instance_a.show_stadium(death_at_game_over=False)
            sleep(0.5)
            system("clear")

    def create_pop(self):
        elite_size = self.pop_n // 4
        
        blue_players = [p for p in self.all_players if p.color == "blue"]
        orange_players = [p for p in self.all_players if p.color == "orange"]
        
        blue_elite = blue_players[:elite_size]
        orange_elite = orange_players[:elite_size]
        
        new_pop_blue = []
        new_pop_orange = []
        
        for i in range(self.pop_n // 2):
            parent1_blue = choice(blue_elite)
            parent2_blue = choice(blue_elite)
            
            parent1_orange = choice(orange_elite)
            parent2_orange = choice(orange_elite)
            
            child_blue = Player_AI("blue", Board(), 3)
            child_blue.brain = parent1_blue.brain.crossover(parent2_blue.brain)
            child_blue.brain.mutate(self.random_ness)
            
            child_orange = Player_AI("orange", Board(), 3)
            child_orange.brain = parent1_orange.brain.crossover(parent2_orange.brain)
            child_orange.brain.mutate(self.random_ness)
            
            new_pop_blue.append(child_blue)
            new_pop_orange.append(child_orange)
        
        self.pop = [new_pop_blue, new_pop_orange]
        
        for player_list in self.pop:
            for player in player_list: player.board = self.board_instance

    def gen_play(self):
        best_overall = None
        best_overall_score = 0
        
        for gen_i in range(self.gen):
            for match_i in range(self.pop_n // 2):
                self.play(match_i)
                
                self.board_instance = Board()
                self.board_instance.players.clear()
            
            best_blue_players = sorted(self.pop[0], key=lambda p: p.score, reverse=True)
            best_orange_players = sorted(self.pop[1], key=lambda p: p.score, reverse=True)
            self.all_players = sorted(best_blue_players+best_orange_players, key=lambda p: p.score, reverse=True)
            
            if best_blue_players and best_blue_players[0].score > best_overall_score:
                best_overall = deepcopy(best_blue_players[0].brain)
                best_overall_score = best_blue_players[0].score

                self.best_overall_match_id = self.pop[0].index(best_blue_players[0])
            
            if best_orange_players and best_orange_players[0].score > best_overall_score:
                best_overall = deepcopy(best_orange_players[0].brain)
                best_overall_score = best_orange_players[0].score
                self.best_overall_match_id = self.pop[1].index(best_orange_players[0])

            self.rewind_game(gen_i)
            self.create_pop()

        print(best_overall_score)
        return best_overall
                    

AI_game = NEAT(200, 30, 2, randomness=0.4)
AI_game.gen_play()
"""
board = Board()
player_blue = Player_AI("blue", board, 3)
player_orange = Player_AI("orange", board, 3)

board.add_player(player_blue)
board.add_player(player_orange)

def demo():
    def test():
        player_blue.move_down()
        player_orange.move_up()
        board.show_stadium()

    def test1():
        player_orange.move_left()
        player_blue.move_down()
        board.show_stadium()
        
    for i in range(5):
        sleep(0.5)
        test()

    for i in range(15):
        sleep(0.5)
        test1()

demo()
"""   