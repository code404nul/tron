"""
DO NOT TEST IN EDUPYTHON (for now)
NE FONCTIONNE PAS SUR PYTHON 3.13 >= (sur linux)

Arch & Renderaction - Tron game on console

Ajouter 10 pts pour chaque mouvements, et 100 pts pour le vainqueur

Pour bouger, vous pouvez faire une remap de touche, par défaut : 
Z/Q/S/D et les fleches pour le deuxième joueurs

TODO direction self colistion
"""

from os import system, path, name # Le system de os est toujours utiliser pour clear la console, et path pour la gestion du chemin pour l'enregistrement du json et name pour detecter si on est sur du linux ou windows
from time import sleep, mktime, localtime, ctime # Time est utiliser pour gerer le temps. ctime for convert sec to date str
import json # La lib json permet de manager les json 
if name == "nt": # Si windows
    is_win = True
    import winsound # Gestion audio
    import msvcrt # Gestion clavier 
else: # Si linux
    is_win = False
    import ossaudiodev #Gestion audio
    import curses # Gestion Clavier 

COLOR = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "orange": "\033[38;5;208m",
    "white": "\033[37m",
    "reset": "\033[0m"
} # Toutes ces valeurs permette de d'afficher des color dans le terminal, je ne l'ai ai pas trouver au hasard, j'ai trouver ca sur internet.


CONFIG_SIZE_Y: int = 27 - 5 # Utiliser pour les border gauche et droit en gros le nombre de character sur la vertical (colone)
CONFIG_FACTOR: int = 2 # Le facteur d'agrandissement pour le border Gauche et droit
CONFIG_SIZE_X: int = CONFIG_SIZE_Y * CONFIG_FACTOR # C'est utilse pour le border haut et bas, car la longeur de chaque cell de charactère et plus petite que la haute des caractere en gros le nombre de character sur l'horizontal (lignes)

class SaveManager:
    def __init__(self, filename="save.json"):
        """
        Docstring for __init__
        
        La classe qui permet d'interagir avec les json
        :param self: Description
        :param filename: De quel json parle ton?
        """
        if not path.exists(filename):
            with open(filename, "w") as f:
                f.write("[]") # Il est nécessaire de mettre une liste vide dans le fichier, sinon quand on dump le json il y aura une erreur 
        with open(filename, "r") as f:
            self.json_data = f.read() 
        self.json_data = json.loads(self.json_data) # transformer le fichier lu comme un txt en json -> dict
            
        self.filename = filename
        
    
    def save(self, data):
        """
        Docstring for save
        
        Va enregistrer data dans le json spécifié
        :param self: Description
        :param data: dict : Les nouvelles data a mettre donc
        
        Return bool, si la save c'est bien passer UwU
        """
        try:
            self.json_data.append(data)
            with open(self.filename, "w") as f:
                f.write(json.dumps(self.json_data, indent=4)) # tout re-ecrire le json précédent + avec le append, le score de cette partie
            return True
        except Exception as e:
            print(f"Aie Aie Aie, une erreur...: {e}")
            return False
    
    def load(self): return self.json_data # Je recupere le contenu du json

class Player:
    def __init__(self, symbol, color, x, y, player_name=None):
        """
        Docstring for __init__
        
        C'est la classe pour un player, il permet de gerer tout ce qui conserne un player personnelement, ces deplacement, sont rendu, ect...
        
        :param self: Description
        :param symbol: Le symbole qui lui sera afficher dans la console
        :param color: La color qui sera afficher quand le player bouge
        :param x: ca positions x
        :param y: ca position y
        :param player_name: le nom du player
        """
        self.symbol = symbol
        self.color = color
        self.x = x
        self.y = y
        self.previous_position = [self.get_pos()] # La previous position contient toutes les positions
        self.path_symbol = "░"
        
        self.player_name = player_name if player_name else f"Player_{color}" # Si le playername n'est pas spécifier, il en crée un nouveau appeler PLayer_couleur.
        self.score = 0
        self.loser = False

        self.current_direction = (0, -1) if color == "blue" else (0, 1)
    
    def get_pos(self): return self.y * CONFIG_SIZE_X + self.x # Quel lignes on est ? * Le nombre de cell par ligne + Les colones ou on est. voir Board.board
    # pas oublier de fetch
    def move(self, dx, dy):
        """
        Docstring for move
        
        Elle mermet d'updater ca position dans ces variables, mais elle verifie aussi que elle ne va pas sur un border
        :param self: Description
        :param dx: pour gauche et droit -1 gauche, 1 droite
        :param dy: pour bas et haut, 1 pour le bas, -1 pour le haut
        
        Return bool, si il y a eu deplacement ou pas.
        """
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        #Verifie Qu'il est dans la grid 1, taille min
        if 1 <= new_x < CONFIG_SIZE_X - 1 and 1 <= new_y < CONFIG_SIZE_Y - 1:
            self.previous_position.append(self.get_pos())
            
            self.x = new_x
            self.y = new_y
            
            self.score += 10
            return True
        return False
    
    # Toutes ces fonctions permet de bouger le player, retourne la meme chose, juste c'est nommé pour que ca soit plus visuel est simple (partique lors de test)
    def move_left(self): return self.move(-1, 0)
    def move_right(self): return self.move(1, 0)
    def move_up(self):  return self.move(0, -1)
    def move_down(self): return self.move(0, 1)
    def move_auto(self): return self.move(self.current_direction)

    def update_direction(self, key): self.current_direction = key

class Board:
    def __init__(self, players=None):
        """
        Cette classe permet de géré les comportement entre player, tel que l'affichage, la detection de colistion, game over,...
        
        players : Peut prendre en parametre du debut des player, mais déconseiller, car veirifie pas que les player s'appelle différament, (ce qui peut provoquer des probleme de nom)
        
        POurquoi pas de changement ? Ca fonctionne donc on touche pas. et c'est pas essentiel 
        
        de base la fonction add_players vient d'un besoin dans main.py, car les joueur_ai on besoin d'un plateau 
        """
        self.board = [] # Tout les caractère afficher sont dans un tableau... Il affiche les charactere du tableau lignes par lignes
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
        """
        Docstring for _create_board
        
        Crée la premiere fonction qui va initaliser la liste self.board, pour afficher les bords.
        
        Ne retourne rien, car update self.board aux seins de l'instance
        """
        self.board = [("#", "white")] * CONFIG_SIZE_X # border du dessus
        
        #Ligne des sides
        for i in range(CONFIG_SIZE_Y - 2):
            self.board.append(("#", "white"))
            self.board += [(" ", "black")] * (CONFIG_SIZE_X - 2)
            self.board.append(("#", "white"))
            
        self.board += [("#", "white")] * CONFIG_SIZE_X #border du dessous
    
    def _check_collision(self):
        """
        Docstring for _check_collision
        
        Cette fonction permet de detecter la colistion, que ca soit sur soit meme, ou sur les autres
        Return bool : Si un des joueurs et censé mourir
        """
        exit_true = False # Le exit_false et utile dans le cas ou 2 player se rentre dessus, plus de prévisition a la prochaine ligne
        for player in self.players:
            
            previous_pos = player.previous_position[1:] # Fix biscornu de position inital qui arrive 2 fois
            
            if (len(previous_pos) != len(set(previous_pos))) and len(previous_pos) > 3: # Verifie si dans les positions y a 2 fois la meme, et verifie si y a eu moins 3 value, toujours le fix biscornu et puis ca sera une feature si le joeur meurt des le debut, ca fonctionne comme ca on touche pas !
                player.loser = True
                return True
            
            for other_player in self.players: #peut etre utile pour du +2 joeurs (cette fonction ne sera jamais implémenté)
                if other_player.player_name != player.player_name:
                    if player.previous_position[-1] in other_player.previous_position: #Si la pos actuelle et dans la pos d'un autre player 
                        player.loser = True
                        exit_true = True # Si 2 player se rentre dessus en meme temps qui a tord? il permet de continuer d'executer la boucle plutot qu'un return.
        
        return exit_true

    def _game_over(self):
        """
        Docstring for _game_over
        
        Lors se que la partie est termine le programme affiche cette ecran. 
        
        Return None
        """
        sleep(1)
        system("clear")
        
        print(f"{COLOR['white']}{self.GAME_OVER_SCREEN}{COLOR['reset']}") # affiche l'ecran de game over
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
        quit() # TODO on devrait revenir sur le menu

    def add_player(self, player): 
        """
        Docstring for add_player
        
        permet de reférencer les player dans la classe. Pour la version main.py, elle est utiliser comme platforme de référence pour connaitre les autres joueurs
        :param player: La classe du player
        
        Return None
        """
        for old_player in self.players:
            if old_player.player_name == player.player_name:
                ValueError("Les noms des joueurs doivent être différents, t'es un fou toi.")
        self.players.append(player)
    
    def show_stadium(self):
        """
        Docstring for show_stadium
        
        Fonction qui va permettre d"afficher le stadium, les player et exec les game over
        doit etre executer A CHAQUE MOUVEMENT 
        
        Return none
        """
        system("clear")
        
        if self._check_collision():
            print("exec game over")
            self._game_over()
            return
        
        for cell in range(len(self.board)): # pour afficher chaque cell
            char, color = self.board[cell]
        
            for p in self.players: #path_symbolr les path_symbols (enfin update juste les valeurs dans la liste)
                if cell in [pos for pos in p.previous_position]:
                    char, color = p.path_symbol, p.color 
                    break
            
            for player in self.players: #path_symbolr la pos actuelle
                if cell == player.get_pos():
                    char, color = player.symbol, player.color
                    break
                
            if (cell + 1) % CONFIG_SIZE_X == 0: #path_symbolr tout le chemil blic (et fait les saut a la lignes)
                print(f"{COLOR[color]}{char}{COLOR['reset']}")
            else:
                print(f"{COLOR[color]}{char}{COLOR['reset']}", end="", flush=True)

        return None

class Input_gestion(): #creation d'une class inputgestion pour stocker les controles des deux joueurs et gerer tout ce qui touche a la detection d'entree clavier

    def __init__(self,tab = None): #les controles des joueurs sont stocker dans une matrice tab de 2x4 pour les 2 joueurs et les 4 touches haut bas gauche droite
        if tab: self.input_table=tab #si tab existe alors self.inputtable prend la valeur de tab
        else: self.input_table = [[95,95,95,95],[95,95,95,95]] #sinon alors self.inputtable devient une matrice remplie de 95 qui correspond en ascii au '_'

    def afficher(self,idjoueur = 3): #une fonction qui affiche de manière esthetique les inputs des joueur
        if idjoueur > 2 or idjoueur < 0: #si l'id du joueur dont on veut print les touches est mal précisé alors la fonction print les touches des 2 joueurs
            print(f"""
Joueur 1
UP:{chr(self.input_table[0][0])}
DOWN:{chr(self.input_table[0][1])}
LEFT:{chr(self.input_table[0][2])}
RIGHT:{chr(self.input_table[0][3])}

Joueur 2
UP:{chr(self.input_table[1][0])}
DOWN:{chr(self.input_table[1][1])}
LEFT:{chr(self.input_table[1][2])}
RIGHT:{chr(self.input_table[1][3])}
""") #les str de type f permette de placer des variables à l'interieur du str avec { } sans devoir concatener

        else: #si l'id est correctement specifié alors on print le joueur voulue
            print(f"""
Joueur {'1' if idjoueur == 0 else '2'}
UP:{chr(self.input_table[idjoueur][0])}
DOWN:{chr(self.input_table[idjoueur][1])}
LEFT:{chr(self.input_table[idjoueur][2])}
RIGHT:{chr(self.input_table[idjoueur][3])}
""")

    def identify_player(self, input_user):
        for i in range(2):
            if input_user in self.input_table[i]:
                return i
        return None
    
    def inputs_windows(self): #cette fonction return la touche pressé sous forme decimal en ascii(ex: si 'z' est pressé alors ça return 122)
        return ord(msvcrt.getwch())


    def inputs_linux(self): #cette fonction fait pareil que inputs_windows() mais en utilisant curses pour linux
        def main(stdscr):
            return stdscr.getch() # 
        return curses.wrapper(main) # 

    def input_common(self):
        if is_win: input_user = self.inputs_windows()
        else: input_user = self.inputs_linux()

        player_id = self.identify_player(input_user)
        return (self.input_table[player_id].index(input_user), player_id)

    def initbindingwin(self):
        for idjoueur in range(2):
            for inp in range(4):
                system("clear")
                self.afficher(idjoueur)
                self.input_table[idjoueur][inp]=ord(msvcrt.getwch())
            self.afficher(idjoueur)
        return self

    def initbindinglinux(self):
        def main(stdscr):
            for idjoueur in range(2):
                for inp in range(4):
                    system("clear")
                    self.afficher(idjoueur)
                    self.input_table[idjoueur][inp]=stdscr.getch()
                self.afficher(idjoueur)
            return self

        if __name__ == '__main__':
            return curses.wrapper(main)     

def demo():
    def test():
        player_blue.move_down()
        player_orange.move_up()
        board_instance.show_stadium()

    def test1():
        player_orange.move_up()
        player_blue.move_down()
        board_instance.show_stadium()
        
    for i in range(9):
        sleep(0.5)
        test()

    for i in range(6):
        sleep(0.5)
        test1()

if __name__=="__main__":
    player_blue = Player("O", "blue", CONFIG_SIZE_X // 2, 1)
    player_orange = Player("O", "orange", CONFIG_SIZE_X // 2, CONFIG_SIZE_Y - 2)

    board_instance = Board()
    board_instance.add_player(player_blue)
    board_instance.add_player(player_orange)
    board_instance.show_stadium()

    demo()