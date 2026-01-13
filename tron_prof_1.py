"""
Ce projet utilise des notions hors programme NSI :
- Threading pour gérer les inputs en temps réel
- Modules système (msvcrt, curses) pour la lecture clavier sans Enter
- ANSI escape codes pour les couleurs terminal
- Détection d'environnement (isatty) pour compatibilité EduPython
"""

"""
DO NOT TEST IN EDUPYTHON (for now)
NE FONCTIONNE PAS SUR PYTHON 3.13 >= (sur linux)

Arch & Renderaction - Tron game on console

Ajouter 10 pts pour chaque mouvements, et 100 pts pour le vainqueur

Pour bouger, vous pouvez faire une remap de touche, par défaut :
Z/Q/S/D et les fleches pour le deuxième joueurs

TODO direction self colistion
"""


"""
(on aurait pu utiliser des arguments mais c'est pas rigolo, surtout si on le lance de base sur powershell)
C'EST QUOI is_atty ?

Avec bryan on s'est posé la question, qu'es qui fait edupython quelque chose de detectable ?
On aurait pu se diriger vers sont interpretateur mais qu'es qui nous dit que vous avez aucun autre interpretateur que edupython ?
Les libs comme lycée serait aussi disponible, il nous faut donc un particularité qui rend spécial notre edupython préféré
un truc, ce petit truc qui le rend different ^^

Donc on s'est penché vers l'affichage, pourquoi edupython affiche pas les couleurs ?
Pourquoi il fait une fenetre tkinter pour les inputs ?

PARCE QUE SONT AFFICHAGE ET ETRANGE, et quand on a un affichage étrange !
On s'est donc penché sur les sys.stdout et sys.stdin car elle permettrait d'apres mon cours sur france IOI d'afficher les charactere, recupere les input plus vite
(Et on devait de base utilser se calvere pour l'affichage avec les inputs linux)

Donc petit passage sur la doc officiel et dit sys.stderr qui nous parle un peu d'erreur
OOOh tiens :

On Windows, UTF-8 is used for the console device. Non-character devices such as disk files and pipes use the system locale encoding (i.e. the ANSI codepage). Non-console character devices such as NUL (i.e. where isatty() returns True) use the value of the console input and output codepages at startup, respectively for stdin and stdout/stderr.
Les saintes paroles sont longues mais disponible ici: https://docs.python.org/3/library/sys.html

Un lundi matin, a la surpirse général le programme ne fonctionnait pas. Pourquoi ? sys.stderr.isatty() ne fonctionnait pas car n'existait pas
Nous avons donc en urgance, trouver ine alternative interne, os.isatty
"""

from random import sample
from os import system, path, name, isatty # Le system de os est toujours utiliser pour clear la console, et path pour la gestion du chemin pour l'enregistrement du json et name pour detecter si on est sur du linux ou windows
from os.path import dirname, abspath, join
from time import sleep, mktime, localtime, time # Time est utiliser pour gerer le temps. ctime for convert sec to date str
from subprocess import call, CREATE_NEW_CONSOLE, Popen
from sys import executable # Pour sys.executable qui donne quel interpreteur python va s'occuper de notre bad boy ^^ et aussi de notre is_atty ?
from pathlib import Path
from pynput import keyboard # le fameux pynput
import json # La lib json permet de manager les json
import threading
import queue


if name == "nt": # Si windows
    is_win = True
    import winsound # Gestion audio
else: # Si linux
    is_win = False
    #import ossaudiodev #Gestion audio


script = Path(__file__).with_name("tron_prof_1.py")

def start_up_powershell():
    system(f"powershell -NoExit -Command \"& '{executable}' '{script}'\"")
    print(f'start powershell -NoExit -Command "& \'{executable}\' \'{script}\'"')

def clear():
    """
    Docstring for clear
    Néttoie l'affichage de la console
    """
    system('cls' if is_win else 'clear') #pour éviter d'écrire system('cls') à chaque fois, on va écrire clear()

COLOR = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "orange": "\033[38;5;208m",
    "white": "\033[37m",
    "black": "\033[30m",
    "reset": "\033[0m"
} # Toutes ces valeurs permette de d'afficher des color dans le terminal, je ne l'ai ai pas trouver au hasard, j'ai trouver ca sur internet.

FPS = 2
CONFIG_SIZE_Y: int = 23  # Utiliser pour les border gauche et droit en gros le nombre de character sur la vertical (colone) Le nombre 23 a été défini parce qu'il est permet d'avoir une grande grille tout en restant raisonable pour etre poser pas trop de problème avec les consoles
CONFIG_FACTOR: int = 2 # Le facteur d'agrandissement pour le border Gauche et droit
CONFIG_SIZE_X: int = CONFIG_SIZE_Y * CONFIG_FACTOR # C'est utilse pour le border haut et bas, car la longeur de chaque cell de charactère et plus petite que la haute des caractere en gros le nombre de character sur l'horizontal (lignes)

ASCIIART = [r"""
 ███████████
▒█▒▒▒███▒▒▒█
▒   ▒███  ▒  ████████   ██████  ████████
    ▒███    ▒▒███▒▒███ ███▒▒███▒▒███▒▒███
    ▒███     ▒███ ▒▒▒ ▒███ ▒███ ▒███ ▒███
    ▒███     ▒███     ▒███ ▒███ ▒███ ▒███
    █████    █████    ▒▒██████  ████ █████
   ▒▒▒▒▒    ▒▒▒▒▒      ▒▒▒▒▒▒  ▒▒▒▒ ▒▒▒▒▒ """, r"""
- Input management, music, menu : Renderaction
- AI system, threading, animation, game system : @archibarbu

This game is under MIT license.
Feel free to contact : perso[aroba]archibarbu[dot]art
Don't hesitate to commit !
Thanks everyone.

          ,'""`.
         / _  _ \
         |(@)(@)|
         )  __  (
        /,'))((`.\
       (( ((  )) ))      hh
        `\ `)(' /'
""", r"""
  ▄████  ▄▄▄       ███▄ ▄███▓▓█████     ▒█████   ██▒   █▓▓█████  ██▀███
 ██▒ ▀█▒▒████▄    ▓██▒▀█▀ ██▒▓█   ▀    ▒██▒  ██▒▓██░   █▒▓█   ▀ ▓██ ▒ ██▒
▒██░▄▄▄░▒██  ▀█▄  ▓██    ▓██░▒███      ▒██░  ██▒ ▓██  █▒░▒███   ▓██ ░▄█ ▒
░▓█  ██▓░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄    ▒██   ██░  ▒██ █░░▒▓█  ▄ ▒██▀▀█▄
░▒▓███▀▒ ▓█   ▓██▒▒██▒   ░██▒░▒████▒   ░ ████▓▒░   ▒▀█░  ░▒████▒░██▓ ▒██▒
 ░▒   ▒  ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░   ░ ▒░▒░▒░    ░ ▐░  ░░ ▒░ ░░ ▒▓ ░▒▓░
  ░   ░   ▒   ▒▒ ░░  ░      ░ ░ ░  ░     ░ ▒ ▒░    ░ ░░   ░ ░  ░  ░▒ ░ ▒░
░ ░   ░   ░   ▒   ░      ░      ░      ░ ░ ░ ▒       ░░     ░     ░░   ░
      ░       ░  ░       ░      ░  ░       ░ ░        ░     ░  ░   ░
                                                     ░                   """]

class SaveManager:
    def __init__(self, filename=None):
        """
        Docstring for __init__

        La classe qui permet d'interagir avec les json
        :param self: Description
        :param filename: De quel json parle ton?"""
        if filename is None:
            script_dir = dirname(abspath(__file__))# IL va recuperer le chemin absolue du sossier ou est le fichier executé
            filename = join(script_dir, "save.json") # Le chemin du fichier actuelle du dossier d'execution + save.json

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
                f.write(json.dumps(self.json_data, indent=4)) # tout re-ecrire le json précédent + avec le append, le score de cette partie, ps le indent permet d'avoir un json lisible, parce que quand on cherchait les bug c'etait pas ouf
            return True
        except Exception as e: # Exception sera l'erreur trouvé par le try.
            print(f"Aie Aie Aie, une erreur...: {e}")
            return False

    def raw_save(self, data):
        """
        Docstring for raw_save
        Va enregistrer data en écrasant dans un json en écrasant tout ce qui se passe BOOM

        :param data: dict : Les nouvelles data a mettre donc!!! (je sais pas pourquoi je suis content, pourquoi mettre !*3 ? UwU )
        """
        with open(self.filename, "w") as f: json.dump(data, f, indent=4)

    def load(self):
        """
        Docstring for load
        return : dict : Les data du json
        """
        return self.json_data

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

        #Verifieque la nouvelle postion x au debut de l'axe x ni début (=0) ni a la fin, meme logique pour y, tout ca dans le but de respectetr les bords
        if 1 <= new_x < CONFIG_SIZE_X - 1 and 1 <= new_y < CONFIG_SIZE_Y - 1:
            self.previous_position.append(self.get_pos())

            self.x = new_x
            self.y = new_y

            self.score += 10
            return True
        return False

    # Toutes ces fonctions permet de bouger le player, retourne la meme chose, juste c'est nommé pour que ca soit plus visuel est simple (partique lors de test) (On m'a dit pas besoin de doc string)
    def move_left(self): return self.move(-1, 0)
    def move_right(self): return self.move(1, 0)
    def move_up(self):  return self.move(0, -1)
    def move_down(self): return self.move(0, 1)

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

    def _create_board(self): #fonction privée
        """
        Docstring for _create_board

        Crée la premiere fonction qui va initaliser la liste self.board, pour afficher les bords.

        Ne retourne rien, car update self.board aux seins de l'instance
        """
        self.board = [("#", "white")] * CONFIG_SIZE_X # créer une premiere ligne de '#' pour representer la bordure de dessus

        #Ligne des sides
        for i in range(CONFIG_SIZE_Y - 2):                              # Boucle pour représenter tout les lignes (en dehors du bord haut et bas) (tout les lignes qui sont comme ca ->  #--------#)
            self.board.append(("#", "white"))                           #
            self.board += [(" ", "black")] * (CONFIG_SIZE_X - 2)        #--------
            self.board.append(("#", "white"))                           #--------#

        self.board += [("#", "white")] * CONFIG_SIZE_X # créer une derniere ligne de '#' pour representer la bordure de dessous

    def _check_collision(self):
        """
        Docstring for _check_collision

        Cette fonction permet de detecter la colistion, que ca soit sur soit meme, ou sur les autres
        Return bool : Si un des joueurs et censé mourir
        """
        exit_true = False # Le exit_false et utile dans le cas ou 2 player se rentre dessus, plus de prévisition a la prochaine ligne
        for player in self.players:

            previous_pos = player.previous_position[1:] # FIX, pb de position 2 current pos et pos initial

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
        clear()

        print(f"{COLOR['white']}{ASCIIART[2]}{COLOR['reset']}") # affiche l'ecran de game over
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
        sleep(4)
        start_up_powershell()
        quit()

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
        clear()

        if self._check_collision():
            print("exec game over")
            self._game_over()
            return

        for cell in range(len(self.board)): # pour afficher chaque cellules
            char, color = self.board[cell]

            for p in self.players: # Pour chaque joueur
                if cell in [pos for pos in p.previous_position]: # Si les case de previous_positon concerne cette case qui s'apprete a etre afficher
                    char, color = p.path_symbol, p.color # Mettre la couleur et le symbole du tracé
                    break

            for player in self.players:
                if cell == player.get_pos(): # si la case concerne la position current du joueur
                    char, color = player.symbol, player.color # Mettre la couleur et le symbole concernant le joueur
                    break
            if (cell + 1) % CONFIG_SIZE_X == 0: # Verifie que c'est le bord
                print(f"{COLOR[color]}{char}{COLOR['reset']}") # retour a la ligne
            else: # sinon
                print(f"{COLOR[color]}{char}{COLOR['reset']}", end="", flush=True) # On affiche les charactere les un apres les autres

        return None

class InputManager():
    def __init__(self, tab=None):
        """creation d'une class InputManager pour stocker les controles des deux joueurs et gerer tout ce qui touche a la detection d'entree clavier"""

        #les controles des joueurs sont stocker dans une matrice tab de 2x4 pour les 2 joueurs et les 4 touches haut bas gauche droite
        if tab: 
            self.input_table = tab #si tab existe alors self.inputtable prend la valeur de tab
        else: 
            # Configuration par défaut: z,s,q,d pour J1 (AZERTY) et i,k,j,l pour J2
            self.input_table = [['z', 's', 'q', 'd'], ['i', 'k', 'j', 'l']]
        
        # Variables pour gérer l'attente d'une touche avec pynput
        self.last_key = None
        self.waiting_for_key = False
        self.key_event = threading.Event()

    def display(self, player_id=3):
        """une fonction qui affiche de manière esthetique les inputs des joueur
        Ne retournz rien"""
        if player_id > 2 or player_id < 0: #si l'id du joueur dont on veut print les touches est mal précisé alors la fonction print les touches des 2 joueurs
            print(f"""
Joueur 1
UP:{self.input_table[0][0]}
DOWN:{self.input_table[0][1]}
LEFT:{self.input_table[0][2]}
RIGHT:{self.input_table[0][3]}

Joueur 2
UP:{self.input_table[1][0]}
DOWN:{self.input_table[1][1]}
LEFT:{self.input_table[1][2]}
RIGHT:{self.input_table[1][3]}
""") #les str de type f permette de placer des variables à l'interieur du str avec { } sans devoir concatener

        else: #si l'id est correctement specifié alors on print le joueur voulue
            print(f"""
Joueur {'1' if player_id == 0 else '2'}
UP:{self.input_table[player_id][0]}
DOWN:{self.input_table[player_id][1]}
LEFT:{self.input_table[player_id][2]}
RIGHT:{self.input_table[player_id][3]}
""")

    def identify_player(self, key_char):
        """
        Docstring pour identify_player

        retorn le joeur concerner
        :param self: Description
        :param key_char: La touche pressée sous forme de caractère
        """
        for i in range(2):
            if key_char in self.input_table[i]: # si l'input préssé et dans la table d'un joueur
                return i # retourner l'indec du joueur
        return None

    def wait_for_key(self):
        """Attend qu'une touche soit pressée et la retourne (avec pynput)"""
        self.last_key = None
        self.waiting_for_key = True
        self.key_event.clear()
        
        def on_press(key):
            if self.waiting_for_key:
                try:
                    self.last_key = key.char
                except AttributeError:
                    self.last_key = str(key)
                self.waiting_for_key = False
                self.key_event.set()
                return False  # Arrête le listener
        
        with keyboard.Listener(on_press=on_press) as listener:
            self.key_event.wait()
        
        return self.last_key

    def initbinding(self):
        """
        Docstring pour initbinding
        Configuration des touches pour les deux joueurs avec pynput
        :param self: Description
        """
        for player_id in range(2):
            for inp in range(4): #parcours par indince du tableau self.input_table
                clear()
                self.display(player_id)
                direction = ["HAUT", "BAS", "GAUCHE", "DROITE"][inp]
                print(f"\nJoueur {player_id + 1} - Appuyez sur la touche pour {direction}")
                
                key = self.wait_for_key() #attend un input exterieur avec pynput, puis le stock
                self.input_table[player_id][inp] = key
            
            self.display(player_id)
        
        return self

    def input_common(self, callback_queue):
        """
        Docstring pour input_common

        retour l'input concerné, dans une fonction multi platforme avec pynput
        :param self: Description
        :param callback_queue: la queue que l'input va traiter
        """
        if callback_queue is None: 
            return self.wait_for_key() # Si aucune queue est concerné par l'histoire alors retourner simplement l'input

        # Fonction pour traiter les événements clavier avec pynput
        def on_press(key):
            try:
                key_char = key.char
            except AttributeError:
                return  # Ignorer les touches spéciales
            
            player_id = self.identify_player(key_char)
            
            if player_id is not None:
                direction_index = self.input_table[player_id].index(key_char)
                result = (direction_index, player_id) # L'index de sur la table de l'input du joueur concerner, et son id
                callback_queue.put(result) # Va mettre le resultat dans la queux a notre start_game_1v1

        # Démarre le listener pynput
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        return listener


class GameManager:
    def __init__(self):
        """
        Docstring for __init__

        La classe qui va gerer le jeu, le menu, les input, ect... c'est un peu le fourre tout (meme si question fourre tout, board est pas mal non plus ^^)
        """
        self.input_config = SaveManager("config.json")
        self.menu_input_config = None
        self.input_manager = None
        self._initialize_input()

    def _initialize_input(self):
        """Initialise la configuration des inputs"""
        try:
            config_data = self.input_config.load()

            # Prendre la première config si c'est une liste, normalement ca l'est
            if isinstance(config_data, list) and len(config_data) > 0:
                layout = config_data[0]["layout"]
            else:
                layout = config_data["layout"]

            self.input_manager = InputManager(layout)
            self.menu_input_config = layout[0]
        except:
            keyboard_layout = input("""
        1. AZERTY?
        2. QWERTY?
        """)
            if int(keyboard_layout) == 1:
                keyboard_keys = ['z', 's', 'q', 'd']  # z, s, q, d
            else:
                keyboard_keys = ['w', 's', 'a', 'd']  # w, s, a, d
            
            self.input_manager = InputManager([keyboard_keys, ['i', 'k', 'j', 'l']])
            self.menu_input_config = keyboard_keys

    def keyboard_settings_menu(self):
        """configutation des touches"""
        clear()
        joueur_temp = InputManager()
        joueur_temp = joueur_temp.initbinding()  # Utilise pynput pour la configuration
        self.input_config.raw_save({"layout": joueur_temp.input_table})
        return joueur_temp

    def credits(self):
        """
        Docstring for credits

        affiche les crédits
        """
        clear()             #clear le terminal
        print(ASCIIART[1])  #print les credits
        self.input_manager.wait_for_key() #stop le programme en attente d'un input clavier pour que l'utilisateur puisse lire les credits et appuyer sur n'importe quel touche pour retourner au menu principal

    def score(self):
        """
        Docstring for score

        affiche les scores
        """
        clear()
        save_manager = SaveManager()
        scores = save_manager.load()

        print(f"{COLOR['red']}=== Top 15 ===\n{COLOR['reset']}")

        liste = []
        for entry in scores:
            for nom, info in entry.items():
                liste.append([nom, info["score"], info["result"], info["date"]])

        for i in range(len(liste)): # trie par insertion
            for j in range(i+1, len(liste)):
                if liste[i][1] < liste[j][1]:
                    liste[i], liste[j] = liste[j], liste[i]

        for i in range(15):
            if i < len(liste):
                print(f"""{COLOR[liste[i][0][7:]]}
╔═ #{i+1:2d} ════════════════════════════
║ Joueur   : {liste[i][0]}
║ Score    : {liste[i][1]} points
║ Résultat : {liste[i][2]}
║ Date     : {liste[i][3]}
╚════════════════════════════════════\n{COLOR['reset']}""")

        self.input_manager.input_common(None) # attendre un input pour retouner au menu


    def run_main_menu(self, menu):
        """
        Affiche le menu et execute ce qu'il faut, il peut retourner (true, joueur) si il a fini c'est qu'il faut lancer le jeu
        """
        selected_index = 0

        while True:
            menu.refresh_menu(selected_index)
            selected_menu = menu.handle_menu_interaction(selected_index, self.menu_input_config)

            if selected_menu == 0:
                start_game_1v1(self.input_manager)

            elif selected_menu == 1:
                self.input_manager = self.keyboard_settings_menu()
                self.menu_input_config = self.input_manager.input_table[0]
                selected_index = selected_menu

            elif selected_menu == 2:
                self.credits()
                selected_index = selected_menu

            elif selected_menu == 3:
                self.score()
                selected_index = selected_menu

    def run(self):
        """Lance le jeu"""
        menu = Menu()
        self.run_main_menu(menu)


class Menu:
    def __init__(self):
        """
        Docstring for __init__

        Cette classe permet de gerer le menu principal
        """
        self.main_interface = f"{COLOR['green']}{ASCIIART[0]}{COLOR['reset']}"

        colors_sample = sample(list(COLOR.keys())[:-2], k=4) # choisi 4 couleurs au hasard pour le menu SANS EN REPRENDRE 1 deja repris dans la liste, on exclu reset et black
        self.selection_list = [
            f"{COLOR[colors_sample[0]]}Démarrer le jeu{COLOR['reset']}",
            f"{COLOR[colors_sample[1]]}Touches Clavier{COLOR['reset']}",
            f"{COLOR[colors_sample[2]]}Credits{COLOR['reset']}",
            f"{COLOR[colors_sample[3]]}Score{COLOR['reset']}"
        ]

    def refresh_menu(self, selected_index=0):
        """affiche le menu avec la selection actuelle"""
        clear()
        print(self.main_interface) #print le logo du jeu
        for i in range(len(self.selection_list)): #parcours les éléments de self.selection_list par indice
            print(f"-[{'*' if selected_index == i else ' '}] {self.selection_list[i]}")

    def handle_menu_interaction(self, selected_index=0, menu_input_config=None):
        """
        gere tout ce qui est navigation dans le menu avec pynput
        return : l'option selectionné
        """
        while True:
            key = None
            key_event = threading.Event()
            
            def on_press(k):
                nonlocal key
                try:
                    key = k.char
                except AttributeError:
                    pass
                key_event.set()
                return False  # Arrête le listener
            
            with keyboard.Listener(on_press=on_press) as listener:
                key_event.wait() #en attente d'une entrée clavier
            
            # valider
            if key == menu_input_config[3]: #touche D (ou équivalent)
                return selected_index

            # aller en HAUT
            elif key == menu_input_config[0]: #touche z ou w en fonction du clavier
                selected_index = (selected_index - 1) % len(self.selection_list)

            # aller en BAS
            elif key == menu_input_config[1]: #touche s
                selected_index = (selected_index + 1) % len(self.selection_list)

            self.refresh_menu(selected_index)

def start_game_1v1(input_manager):
    """
    Docstring for start_game_1v1
    Cette fonction lance une partie de tron en 1v1

    :param input_manager: La classe qui va gerer tout ce bazar d'input
    Return rien du tout puisque c'est une boucle infinie qui se fini par un quit() méchant
    """
    player_blue = Player("O", "blue", CONFIG_SIZE_X // 2, 1)  # haut au centre
    player_orange = Player("O", "orange", CONFIG_SIZE_X // 2, CONFIG_SIZE_Y - 2)  # bas au centre

    board_instance = Board()

    board_instance.add_player(player_blue)
    board_instance.add_player(player_orange)

    callback_queue = queue.Queue() # Queue pour gerer la queue d'input, ca va permettre de pouvoir "fait tourner le jeu" et de recuperer les inputs en meme temps (threading) et la queue va permettre a ce que chaque frame, le programme puisse traiter les inputs detectés.

    # mapping des directions
    DIRECTION_MAP = {
        0: (0, -1),  # Haut
        1: (0, 1),   # Bas
        2: (-1, 0),  # Gauche
        3: (1, 0)    # Droite
    }
    
    board_instance.show_stadium()
    last_move_time = 0

    # Démarre le listener avec pynput
    listener = input_manager.input_common(callback_queue)

    while True:

        while not callback_queue.empty(): # traiter les inputs dispo
            try:
                # Recupere un msg sans attendre
                callback_message = callback_queue.get_nowait()

                direction, player_id = callback_message
                dx, dy = DIRECTION_MAP[direction]

                if player_id == 0: # cahnger la direction du joueur concerné
                    player_blue.current_direction = (dx, dy)
                elif player_id == 1:
                    player_orange.current_direction = (dx, dy)

            except queue.Empty: # PLus d'input
                break

        current_time = time()
        if current_time - last_move_time >= (1/FPS): # Tout les 0.5 un peu pres refaire une image donc 2 fps

            # continuer de bouger dans la meme direction
            dx_blue, dy_blue = player_blue.current_direction
            player_blue.move(dx_blue, dy_blue)

            dx_orange, dy_orange = player_orange.current_direction
            player_orange.move(dx_orange, dy_orange)

            board_instance.show_stadium()

            last_move_time = current_time

        # Petit pause pour sont petit coeur
        sleep(0.01)

def main():
    game_manager = GameManager()
    game_manager.run()


if not isatty(1): # Le 1 et pour verrifier dans stdout, il verifie que la sortie et un terminal conventionnel
    start_up_powershell()
    if is_win:
        winsound.PlaySound('tronost.wav', winsound.SND_FILENAME | winsound.SND_LOOP) # lance une musique, loupé
else:
    main()


"""

RAPPORT AUTOMATISE :

# Rapport d'analyse du code Tron

## Vue d'ensemble
Ce projet est une implémentation du jeu Tron en console Python, développé par deux étudiants (Renderaction et @archibarbu). Le jeu permet à deux joueurs de s'affronter en temps réel dans un terminal, chacun laissant une traînée derrière lui. Le premier qui percute un obstacle perd.

## Points forts

### Architecture logique
Le code suit une structure orientée objet claire avec des responsabilités bien séparées :
- `Player` : gestion individuelle des joueurs
- `Board` : gestion du plateau et des collisions
- `InputManager` : capture des entrées clavier
- `GameManager` : orchestration générale
- `SaveManager` : persistance des données

### Fonctionnalités complètes
- Menu principal avec navigation
- Configuration personnalisable des touches
- Système de score avec sauvegarde JSON
- Écran de crédits
- Détection de collisions (murs, adversaire, soi-même)
- Gestion multi-thread pour les inputs en temps réel

### Détails techniques intéressants
- Utilisation de threads pour gérer les entrées sans bloquer le rendu
- Système de queue pour synchroniser les inputs avec la boucle de jeu
- Détection intelligente de l'environnement (EduPython, Windows/Linux)
- Codes ANSI pour les couleurs dans le terminal

## Points à améliorer

### Maintenabilité du code
**Commentaires excessifs et redondants** : Le code contient beaucoup de commentaires en français mélangeant explications, blagues et notes personnelles, ce qui nuit à la lisibilité professionnelle.

**Constantes magiques** : Plusieurs valeurs hardcodées (FPS=2, scores de 10 et 100 points) devraient être des constantes nommées ou configurables.

**Gestion d'erreurs limitée** : Le try-except dans `_initialize_input()` capture toutes les exceptions sans distinction, masquant potentiellement des bugs.

### Problèmes de conception

**Support Linux incomplet** : Toutes les fonctions Linux sont des `pass`, rendant le jeu Windows-only malgré les efforts de détection multiplateforme.

**Couplage fort** : `Board._game_over()` lance directement un nouveau processus PowerShell, ce qui est très peu portable et crée un couplage inattendu.

**Thread non stoppable** : Le thread d'écoute des inputs n'a pas de mécanisme d'arrêt propre, tournant indéfiniment en arrière-plan.

### Bugs et comportements étranges

**Fix "biscornu"** : Les développeurs eux-mêmes reconnaissent un bug dans `_check_collision()` avec la vérification `len(previous_pos) > 3`, indiquant une solution temporaire non optimale.

**Démarrage en boucle** : La fonction `_game_over()` relance automatiquement le jeu via PowerShell au lieu de retourner au menu, créant une boucle sans fin de processus.

**Détection EduPython fragile** : L'utilisation de `isatty()` pour détecter EduPython est un hack astucieux mais peu fiable à long terme.

### Performance et optimisation
- Recréation complète du board à chaque frame plutôt que mise à jour incrémentale
- Utilisation de `sleep(0.01)` dans la boucle principale qui pourrait être optimisée
- Conversion répétée de positions avec `get_pos()` pourrait être mise en cache

## Recommandations prioritaires

1. **Simplifier la documentation** : Réduire les commentaires au strict nécessaire, retirer les blagues et notes personnelles
2. **Finaliser le support Linux** : Implémenter curses pour avoir un vrai jeu multiplateforme
3. **Nettoyer le game over** : Retourner au menu au lieu de créer des processus infinis
4. **Améliorer la gestion d'erreurs** : Utiliser des exceptions spécifiques et des messages clairs
5. **Ajouter un système de configuration** : Externaliser FPS, scores, et dimensions du plateau

## Conclusion
Ce projet montre une bonne compréhension des concepts de programmation orientée objet et de gestion d'événements en temps réel. L'ambition est louable (multiplateforme, threading, sauvegarde) mais l'exécution souffre de quelques raccourcis et de fonctionnalités inachevées. Avec un peu de nettoyage et la finalisation du support Linux, ce pourrait être un excellent projet pédagogique. Le code fonctionne mais gagnerait en professionnalisme avec une documentation plus sobre et une architecture légèrement refactorisée.
"""
