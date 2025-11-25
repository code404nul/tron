"""
▗▄▄▄   ▄▄▄      ▄▄▄▄   ▄▄▄     ■         ■  ▗▞▀▚▖ ▄▄▄  ■      ▄ ▄▄▄▄      ▗▞▀▚▖   ▐▌█  ▐▌▄▄▄▄  ▄   ▄    ■  ▐▌    ▄▄▄  ▄▄▄▄  
▐▌  █ █   █     █   █ █   █ ▗▄▟▙▄▖    ▗▄▟▙▄▖▐▛▀▀▘▀▄▄▗▄▟▙▄▖    ▄ █   █     ▐▛▀▀▘   ▐▌▀▄▄▞▘█   █ █   █ ▗▄▟▙▄▖▐▌   █   █ █   █ 
▐▌  █ ▀▄▄▄▀     █   █ ▀▄▄▄▀   ▐▌        ▐▌  ▝▚▄▄▖▄▄▄▀ ▐▌      █ █   █     ▝▚▄▄▖▗▞▀▜▌     █▄▄▄▀  ▀▀▀█   ▐▌  ▐▛▀▚▖▀▄▄▄▀ █   █ 
▐▙▄▄▀                         ▐▌        ▐▌            ▐▌      █                ▝▚▄▟▌     █     ▄   █   ▐▌  ▐▌ ▐▌            

Système NEAT complet pour entraîner des IA au jeu Tron
"""

from math import log2, exp
from random import uniform, choice, random
from os import system, get_terminal_size, path
from time import sleep, mktime, localtime
import json

# ==================== CONFIGURATION ====================
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

CONFIG_SIZE = get_terminal_size().lines - 5
CONFIG_FACTOR = 2
CONFIG_REAL_SIZE = CONFIG_SIZE * CONFIG_FACTOR


# ==================== RÉSEAU DE NEURONES ====================
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
        
        # Couches cachées
        for _ in range(self.depth - 1):
            W = [[uniform(-1, 1) for _ in range(self.width)] for _ in range(self.width)]
            b = [[uniform(-1, 1) for _ in range(self.width)]]
            self.layers.append((W, b))
        
        # Couche output (4 directions)
        W = [[uniform(-1, 1) for _ in range(4)] for _ in range(self.width)]
        b = [[uniform(-1, 1) for _ in range(4)]]
        self.layers.append((W, b))
        
        self.fitness = 0
    
    def sigmoid(self, x):
        return 1 / (1 + exp(-max(-500, min(500, x))))
    
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
        current = X
        for W, b in self.layers:
            z = self.mul_tableau(current, W)
            z = self.ajout_biais(z, b)
            current = [[self.sigmoid(z[i][j]) for j in range(len(z[0]))] for i in range(len(z))]
        return current
    
    def predict(self, inputs):
        """Prédit la meilleure action (0=gauche, 1=droite, 2=haut, 3=bas)"""
        output = self.forward([inputs])
        return output[0].index(max(output[0]))
    
    def mutate(self, mutation_rate=0.1, mutation_strength=0.3):
        """Mute les poids et biais"""
        for i, (W, b) in enumerate(self.layers):
            for j in range(len(W)):
                for k in range(len(W[0])):
                    if random() < mutation_rate:
                        W[j][k] += uniform(-mutation_strength, mutation_strength)
            
            for k in range(len(b[0])):
                if random() < mutation_rate:
                    b[0][k] += uniform(-mutation_strength, mutation_strength)
            
            self.layers[i] = (W, b)
    
    def crossover(self, other):
        """Crée un enfant en croisant deux réseaux"""
        child = NeuralNetwork(len(self.layers[0][0]), self.learning_rate)
        
        for i in range(len(self.layers)):
            W_self, b_self = self.layers[i]
            W_other, b_other = other.layers[i]
            W_child, b_child = child.layers[i]
            
            for j in range(len(W_child)):
                for k in range(len(W_child[0])):
                    W_child[j][k] = W_self[j][k] if random() < 0.5 else W_other[j][k]
            
            for k in range(len(b_child[0])):
                b_child[0][k] = b_self[0][k] if random() < 0.5 else b_other[0][k]
            
            child.layers[i] = (W_child, b_child)
        
        return child


# ==================== JOUEUR IA ====================
class Player_AI_NN:
    """IA contrôlée par un réseau de neurones"""
    def __init__(self, symbol, color, x, y, board, brain=None, player_name=None):
        self.symbol = symbol
        self.color = color
        self.x = x
        self.y = y
        self.previous_position = [self.get_pos()]
        self.trace = "░"
        
        self.player_name = player_name if player_name else f"AI_{color}"
        self.score = 0
        self.loser = False
        
        self.board = board
        
        # Cerveau : réseau de neurones
        # Inputs: 8 directions + 2 coords adversaire + 2 coords propres = 12 inputs
        self.brain = brain if brain else NeuralNetwork(input_size=12)
    
    def get_pos(self):
        return self.y * CONFIG_REAL_SIZE + self.x
    
    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 1 <= new_x < CONFIG_REAL_SIZE - 1 and 1 <= new_y < CONFIG_SIZE - 1:
            self.previous_position.append(self.get_pos())
            self.x = new_x
            self.y = new_y
            self.score += 10
            return True
        return False
    
    def get_vision(self):
        """Obtient les infos sur l'environnement (8 directions)"""
        directions = [
            (0, -1), (1, -1), (1, 0), (1, 1),
            (0, 1), (-1, 1), (-1, 0), (-1, -1)
        ]
        
        vision = []
        for dx, dy in directions:
            check_x, check_y = self.x + dx, self.y + dy
            check_pos = check_y * CONFIG_REAL_SIZE + check_x
            
            is_blocked = 0
            if (check_x <= 0 or check_x >= CONFIG_REAL_SIZE - 1 or 
                check_y <= 0 or check_y >= CONFIG_SIZE - 1):
                is_blocked = 1
            else:
                for player in self.board.players:
                    if check_pos in player.previous_position:
                        is_blocked = 1
                        break
            
            vision.append(is_blocked)
        
        # Position relative adversaire
        opponent = None
        for player in self.board.players:
            if player.player_name != self.player_name:
                opponent = player
                break
        
        if opponent:
            rel_x = (opponent.x - self.x) / CONFIG_REAL_SIZE
            rel_y = (opponent.y - self.y) / CONFIG_SIZE
        else:
            rel_x, rel_y = 0, 0
        
        # Position propre normalisée
        norm_x = self.x / CONFIG_REAL_SIZE
        norm_y = self.y / CONFIG_SIZE
        
        return vision + [rel_x, rel_y, norm_x, norm_y]
    
    def think(self):
        """L'IA décide de son prochain mouvement"""
        inputs = self.get_vision()
        action = self.brain.predict(inputs)
        
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = moves[action]
        success = self.move(dx, dy)
        
        # Si échec, essayer alternative
        if not success:
            for alt_dx, alt_dy in moves:
                if (alt_dx, alt_dy) != (dx, dy):
                    if self.move(alt_dx, alt_dy):
                        break
    
    def render(self):
        return f"{COLOR[self.color]}{self.symbol}{COLOR['reset']}"


# ==================== PLATEAU DE JEU ====================
class Board:
    def __init__(self):
        self.board = []
        self._create_board()
        self.players = []
        
        self.GAME_OVER_SCREEN = """
  ▄████  ▄▄▄       ███▄ ▄███▓▓█████     ▒█████   ██▒   █▓▓█████  ██▀███  
 ██▒ ▀█▒▒████▄    ▓██▒▀█▀ ██▒▓█   ▀    ▒██▒  ██▒▓██░   █▒▓█   ▀ ▓██ ▒ ██▒
▒██░▄▄▄░▒██  ▀█▄  ▓██    ▓██░▒███      ▒██░  ██▒ ▓██  █▒░▒███   ▓██ ░▄█ ▒
░▓█  ██▓░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄    ▒██   ██░  ▒██ █░░▒▓█  ▄ ▒██▀▀█▄  
░▒▓███▀▒ ▓█   ▓██▒▒██▒   ░██▒░▒████▒   ░ ████▓▒░   ▒▀█░  ░▒████▒░██▓ ▒██▒"""
    
    def _create_board(self):
        self.board = [("#", "white")] * CONFIG_REAL_SIZE
        
        for i in range(CONFIG_SIZE - 2):
            self.board.append(("#", "white"))
            self.board += [(" ", "black")] * (CONFIG_REAL_SIZE - 2)
            self.board.append(("#", "white"))
            
        self.board += [("#", "white")] * CONFIG_REAL_SIZE
    
    def _check_collision(self):
        for player in self.players:
            previous_pos = player.previous_position[1:]
            
            if len(previous_pos) != len(set(previous_pos)) and len(previous_pos) > 3:
                player.loser = True
                return True
            
            for other_player in self.players:
                if other_player.player_name != player.player_name:
                    if player.previous_position[-1] in other_player.previous_position:
                        player.loser = True
                        return True
        
        return False
    
    def add_player(self, player):
        self.players.append(player)
    
    def show_stadium(self, show_display=True):
        """Affiche le plateau (optionnel pour training rapide)"""
        if not show_display:
            return
            
        system("clear")
        
        if self._check_collision():
            return
        
        for case in range(len(self.board)):
            char, color = self.board[case]
        
            for p in self.players:
                if case in p.previous_position:
                    char, color = p.trace, p.color
                    break
            
            for player in self.players:
                if case == player.get_pos():
                    char, color = player.symbol, player.color
                    break
                
            if (case + 1) % CONFIG_REAL_SIZE == 0:
                print(f"{COLOR[color]}{char}{COLOR['reset']}")
            else:
                print(f"{COLOR[color]}{char}{COLOR['reset']}", end="", flush=True)


# ==================== ENTRAÎNEUR NEAT ====================
class NEATTrainer:
    """Gestionnaire d'évolution pour les IA"""
    def __init__(self, population_size=20):
        self.population_size = population_size
        self.generation = 0
        self.population = [NeuralNetwork(input_size=12) for _ in range(population_size)]
        self.best_fitness_history = []
        self.avg_fitness_history = []
    
    def evaluate_population(self, games_per_pair=3, max_moves=500):
        """Évalue chaque réseau en le faisant jouer"""
        for brain in self.population:
            brain.fitness = 0
        
        for i in range(0, len(self.population), 2):
            if i + 1 < len(self.population):
                brain1 = self.population[i]
                brain2 = self.population[i + 1]
                
                for game in range(games_per_pair):
                    self._play_game(brain1, brain2, max_moves)
    
    def _play_game(self, brain1, brain2, max_moves):
        """Simule une partie entre deux IA"""
        board = Board()
        
        player1 = Player_AI_NN("O", "blue", CONFIG_REAL_SIZE // 2, 1, 
                               board, brain1, "AI1")
        player2 = Player_AI_NN("X", "orange", CONFIG_REAL_SIZE // 2, CONFIG_SIZE - 2,
                               board, brain2, "AI2")
        
        board.add_player(player1)
        board.add_player(player2)
        
        moves = 0
        game_over = False
        
        while not game_over and moves < max_moves:
            player1.think()
            player2.think()
            
            if board._check_collision():
                game_over = True
            
            moves += 1
        
        # Attribuer fitness
        if player1.loser and not player2.loser:
            brain1.fitness += player1.score
            brain2.fitness += player2.score + 500
        elif player2.loser and not player1.loser:
            brain1.fitness += player1.score + 500
            brain2.fitness += player2.score
        else:
            brain1.fitness += player1.score
            brain2.fitness += player2.score
    
    def evolve(self):
        """Crée la nouvelle génération"""
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        
        best_fitness = self.population[0].fitness
        avg_fitness = sum(brain.fitness for brain in self.population) / len(self.population)
        
        self.best_fitness_history.append(best_fitness)
        self.avg_fitness_history.append(avg_fitness)
        
        print(f"\n{'='*50}")
        print(f"🧬 Génération {self.generation}")
        print(f"{'='*50}")
        print(f"🏆 Meilleur fitness: {best_fitness:.2f}")
        print(f"📊 Fitness moyen: {avg_fitness:.2f}")
        
        # Élitisme
        elite_size = self.population_size // 5
        new_population = self.population[:elite_size]
        
        # Reproduction
        while len(new_population) < self.population_size:
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            child = parent1.crossover(parent2)
            child.mutate(mutation_rate=0.15, mutation_strength=0.4)
            
            new_population.append(child)
        
        self.population = new_population
        self.generation += 1
    
    def _tournament_selection(self, tournament_size=3):
        """Sélection par tournoi"""
        tournament = [choice(self.population[:self.population_size // 2]) 
                     for _ in range(tournament_size)]
        return max(tournament, key=lambda x: x.fitness)
    
    def save_best(self, filename="best_brain.json"):
        """Sauvegarde le meilleur réseau"""
        best = self.population[0]
        data = {
            "generation": self.generation,
            "fitness": best.fitness,
            "layers": [{"weights": W, "bias": b} for W, b in best.layers]
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"💾 Sauvegardé: {filename}")
    
    def visualize_best(self, num_games=1):
        """Visualise le meilleur agent"""
        best_brain = self.population[0]
        
        for game_num in range(num_games):
            board = Board()
            opponent_brain = NeuralNetwork(input_size=12)
            
            player1 = Player_AI_NN("🔵", "blue", CONFIG_REAL_SIZE // 2, 2, 
                                   board, best_brain, "Champion")
            player2 = Player_AI_NN("🔴", "red", CONFIG_REAL_SIZE // 2, CONFIG_SIZE - 3,
                                   board, opponent_brain, "Challenger")
            
            board.add_player(player1)
            board.add_player(player2)
            
            moves = 0
            max_moves = 300
            
            while moves < max_moves:
                system("clear")
                print(f"🎮 Partie {game_num + 1} - Mouvement {moves}")
                print(f"🔵 Champion: {player1.score} | 🔴 Challenger: {player2.score}\n")
                
                board.show_stadium(show_display=True)
                
                player1.think()
                player2.think()
                
                if board._check_collision():
                    if player1.loser:
                        print("\n💔 Champion perdu!")
                    else:
                        print("\n🎉 Champion victorieux!")
                    sleep(2)
                    break
                
                moves += 1
                sleep(0.05)


# ==================== MENU PRINCIPAL ====================
def train_ai(generations=100, population_size=20, games_per_pair=3, 
             max_moves=500, visualize_interval=20):
    """Lance l'entraînement"""
    
    trainer = NEATTrainer(population_size=population_size)
    
    print("""
    ╔════════════════════════════════════════╗
    ║   🤖 ENTRAÎNEMENT IA - TRON GAME      ║
    ╚════════════════════════════════════════╝
    """)
    print(f"Population: {population_size}")
    print(f"Générations: {generations}")
    print(f"Parties par paire: {games_per_pair}\n")
    
    try:
        for gen in range(generations):
            print(f"\n⚙️  Entraînement génération {gen}...")
            trainer.evaluate_population(games_per_pair, max_moves)
            trainer.evolve()
            
            if gen % 10 == 0 and gen > 0:
                trainer.save_best(f"brain_gen_{gen}.json")
            
            if gen % visualize_interval == 0 and gen > 0:
                print("\n🎮 Démonstration du champion:")
                trainer.visualize_best(num_games=1)
        
        trainer.save_best("best_brain_final.json")
        
        print("\n" + "="*50)
        print("✅ ENTRAÎNEMENT TERMINÉ!")
        print("="*50)
        print(f"Amélioration totale: {trainer.best_fitness_history[-1] - trainer.best_fitness_history[0]:.2f}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompu - Sauvegarde...")
        trainer.save_best("brain_interrupted.json")


def play_with_trained():
    """Charge et joue avec une IA entraînée"""
    filename = input("Fichier brain (défaut: best_brain_final.json): ") or "best_brain_final.json"
    
    if not path.exists(filename):
        print(f"❌ Fichier {filename} introuvable!")
        return
    
    with open(filename, "r") as f:
        data = json.load(f)
    
    brain = NeuralNetwork(input_size=12)
    for i, layer_data in enumerate(data["layers"]):
        brain.layers[i] = (layer_data["weights"], layer_data["bias"])
    
    print(f"✅ Cerveau chargé - Gen {data['generation']}, Fitness: {data['fitness']:.2f}\n")
    
    trainer = NEATTrainer(population_size=1)
    trainer.population = [brain]
    trainer.visualize_best(num_games=5)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║      🎮 TRON AI - MENU PRINCIPAL      ║
    ╚════════════════════════════════════════╝
    
    1. 🚀 Entraînement rapide (50 gen, 30 pop)
    2. 💪 Entraînement intense (200 gen, 50 pop)
    3. 🎯 Entraînement personnalisé
    4. 👀 Visualiser IA entraînée
    5. ❌ Quitter
    """)
    
    choice = input("Choix: ")
    
    if choice == "1":
        train_ai(generations=50, population_size=30, visualize_interval=10)
    
    elif choice == "2":
        train_ai(generations=200, population_size=50, visualize_interval=25)
    
    elif choice == "3":
        gen = int(input("Nombre de générations: "))
        pop = int(input("Taille population: "))
        train_ai(generations=gen, population_size=pop)
    
    elif choice == "4":
        play_with_trained()
    
    else:
        print("Au revoir! 👋")