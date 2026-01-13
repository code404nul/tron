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
from time import sleep, mktime, localtime # Time est utiliser pour gerer le temps. ctime for convert sec to date str
from sys import executable # Pour sys.executable qui donne quel interpreteur python va s'occuper de notre bad boy ^^ et aussi de notre is_atty ?
from pathlib import Path
import json

from matplotlib.pylab import char # La lib json permet de manager les json
if name == "nt": # Si windows
    is_win = True
    import winsound # Gestion audio


import sys # Pour sys.executable qui donne quel interpreteur python va s'occuper de notre bad boy ^^ et aussi de notre is_atty ?

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
    pass

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

        print(f"{ASCIIART[2]}") # affiche l'ecran de game over
        sleep(1)

        game_data = {}
        date = mktime(localtime())

        for player in self.players:
            if player.loser:
                print(f"{player.player_name} LOSE! Score: {player.score}")
                game_data[player.player_name] = {
                    "score": player.score,
                    "result": "lose",
                    "mouvements": player.previous_position,
                    "date": date
                }
            else:
                player.score += 100
                print(f"{player.player_name} WIN! Score: {player.score}")
                game_data[player.player_name] = {
                    "score": player.score,
                    "result": "win",
                    "mouvements": player.previous_position,
                    "date": date
                }

        self.save_manager.save(game_data)
        sleep(4)
        system(f"start powershell.exe {sys.executable} {join(dirname(abspath(__file__)), 'tron_prof.py')}")
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
                    char, color = player.symbol, player.color # Mettre dla couleur et le symbole concernant le joueur
                    break
            if (cell + 1) % CONFIG_SIZE_X == 0: # Verifie que c'est le bord 
                print(f"{char}") # retour a la ligne
            else: # sinon
                print(f"{char}", end="", flush=True) # On affiche les charactere les un apres les autres L INTERPRETEUR EDUPYTHON NE PEUX PAS LIRE CE FICHIER ESSAYER tron_prof_3.py
        return None

class InputManager(): #creation d'une class InputManager pour stocker les controles des deux joueurs et gerer tout ce qui touche a la detection d'entree clavier

    def __init__(self):
        self.input_config_save = SaveManager("config_2.json")
        self.input_config_value = self.input_config_save.load()
        if isinstance(self.input_config_value, dict):
            self.input_config_value = self.input_config_value["layout"]
        else:
            self.input_config_value = self.input_config_value
        self.input_table = [["z", "s", "q", "d"], ["i", "k", "j", "l"]]
        if len(self.input_config_value) != 0:
            self.input_table = self.input_config_value
        print(self.input_table)
        
    def input_config(self):
        for i in range(2):
            for a, direction in enumerate(["HAUT", "BAS", "GAUCHE", "DROITE"]):
                clear()
                print(f"Pour Joueur {i+1} : ")
                print(f"Entrer l'input pour : {direction}")
                print("Oublier pas entrer")
                self.input_table[i][a] = input()
        self.input_config_save.raw_save(self.input_table)
        
    def identify_player(self, inputs):
        for i in range(2):
            if inputs in self.input_table[i]:
                return (i, self.input_table[i].index(inputs))
        return None

    def read_inputs(self, get_players_info=False):
        inputs = list(input())
        if not get_players_info: return inputs
        else:
            actions = []
            for ele in inputs:
                action = self.identify_player(ele)
                if action: actions.append(action)

        return actions

class GameManager:
    def __init__(self):
        """
        Docstring for __init__

        La classe qui va gerer le jeu, le menu, les input, ect... c'est un peu le fourre tout (meme si question fourre tout, board est pas mal non plus ^^)
        """
        self.input_manager = InputManager()

    def credits(self):
        """
        Docstring for credits
        
        affiche les crédits
        """
        clear()             #clear le terminal
        print(ASCIIART[1])  #print les credits
        input()

    def score(self):
        """
        Docstring for score
        
        affiche les scores
        """
        clear()
        save_manager = SaveManager()
        scores = save_manager.load()

        print(f"=== Top 15 ===\n")

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
                print(f"""
╔═ #{i+1:2d} ════════════════════════════
║ Joueur   : {liste[i][0]}
║ Score    : {liste[i][1]} points
║ Résultat : {liste[i][2]}
║ Date     : {liste[i][3]}
╚════════════════════════════════════\n""")

        input()

    def run_main_menu(self, menu):
        """
        Affiche le menu et execute ce qu'il faut, il peut retourner (true, joueur) si il a fini c'est qu'il faut lancer le jeu
        """
        selected_index = 0

        while True:
            menu.refresh_menu(selected_index)
            selected_menu = menu.handle_menu_interaction(selected_index, self.input_manager)

            if selected_menu == 0:
                start_game_1v1(self.input_manager)

            elif selected_menu == 1:
                self.input_manager.input_config()

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
        self.main_interface = f"{ASCIIART[0]}"

        self.selection_list = [
            f"Démarrer le jeu",
            f"Touches Clavier",
            f"Credits",
            f"Score"
        ]

    def refresh_menu(self, selected_index=0):
        """affiche le menu avec la selection actuelle"""
        clear()
        print(self.main_interface)
        for i in range(len(self.selection_list)):
            print(f"-[{'*' if selected_index == i else ' '}] {self.selection_list[i]}")

    def handle_menu_interaction(self, selected_index=0, input_manager=None):
        """
        gere tout ce qui est navigation dans le menu
        reuturn : l'optiuon selectionné
        """

        while True:

            pinput = input_manager.read_inputs(True)
            print(pinput)
            pinput = pinput[0][1]
                # valider
            if pinput == 3:  # Droite
                return selected_index

                # aller en HAUT
            elif pinput == 0:
                selected_index = (selected_index - 1) % len(self.selection_list)

                # aller en BAS
            elif pinput in [1, 2]:
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

    # mapping des directions
    DIRECTION_MAP = {
        0: (0, -1),  # Haut
        1: (0, 1),   # Bas
        2: (-1, 0),  # Gauche
        3: (1, 0)    # Droite
    }
    board_instance.show_stadium()


    move_player = [False, False]
    while True:

        received_inputs = input_manager.read_inputs(True)
        
        for inputs in received_inputs:
            player_id, direction = inputs
            print(f"Player {player_id} direction {direction}")
            dx, dy = DIRECTION_MAP[direction]
            print(f"dx: {dx}, dy: {dy}")

            if player_id == 0:
                player_blue.current_direction = (dx, dy)
                move_player[0] = True
            elif player_id == 1:
                player_orange.current_direction = (dx, dy)
                move_player[1] = True

        if move_player[0] and move_player[1]:
            dx_blue, dy_blue = player_blue.current_direction
            player_blue.move(dx_blue, dy_blue)

            dx_orange, dy_orange = player_orange.current_direction
            player_orange.move(dx_orange, dy_orange)

            board_instance.show_stadium()
            move_player = [False, False]
    
def main():
    game_manager = GameManager()
    game_manager.run()

"""
input_manager = InputManager()
while True:
    print(input_manager.read_inputs(True))
"""

if not isatty(1): # Le 1 et pour verrifier dans stdout, il verifie que la sortie et un terminal conventionnel
    system(f"start powershell.exe {sys.executable} {join(dirname(abspath(__file__)), 'tron_prof_2.py')}")
    winsound.PlaySound('tronost.wav', winsound.SND_FILENAME | winsound.SND_LOOP) # lance une musique, loupé
else:
    main()


"""

RAPPORT AUTOMATISE :

"""
