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
"""

import curses
from random import sample
from os import system, path, name, getcwd # Le system de os est toujours utiliser pour clear la console, et path pour la gestion du chemin pour l'enregistrement du json et name pour detecter si on est sur du linux ou windows
from os.path import dirname, abspath, join
from time import sleep, mktime, localtime, time # Time est utiliser pour gerer le temps. ctime for convert sec to date str
import json # La lib json permet de manager les json
if name == "nt": # Si windows
    is_win = True
    import winsound # Gestion audio
    import msvcrt # Gestion clavier
"""
else: # Si linux
    is_win = False
    #import ossaudiodev #Gestion audio
    import curses # Gestion Clavier
"""


import sys # Pour sys.executable qui donne quel interpreteur python va s'occuper de notre bad boy ^^ et aussi de notre is_atty ?
import threading
import queue


clear= lambda: system('cls' if name == 'nt' else 'clear') #pour éviter d'écrire system('cls') à chaque fois, on va écrire clear()

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
            script_dir = dirname(abspath(__file__))
            filename = join(script_dir, "save.json")

        self.filename = filename

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

        #Verifie Qu'il est dans la grid 1, taille min
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

class InputManager(): #creation d'une class InputManager pour stocker les controles des deux joueurs et gerer tout ce qui touche a la detection d'entree clavier

    def __init__(self,tab = None): #les controles des joueurs sont stocker dans une matrice tab de 2x4 pour les 2 joueurs et les 4 touches haut bas gauche droite
        if tab: self.input_table=tab #si tab existe alors self.inputtable prend la valeur de tab
        else: self.input_table = [[122,115,113,100],[105, 107, 106, 108]] #sinon alors self.inputtable devient une matrice remplie de 95 qui correspond en ascii au '_'

    def display(self,player_id = 3): #une fonction qui affiche de manière esthetique les inputs des joueur
        if player_id > 2 or player_id < 0: #si l'id du joueur dont on veut print les touches est mal précisé alors la fonction print les touches des 2 joueurs
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
Joueur {'1' if player_id == 0 else '2'}
UP:{chr(self.input_table[player_id][0])}
DOWN:{chr(self.input_table[player_id][1])}
LEFT:{chr(self.input_table[player_id][2])}
RIGHT:{chr(self.input_table[player_id][3])}
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


    def initbindingwin(self):
        for player_id in range(2):
            for inp in range(4):
                clear()
                self.display(player_id)
                self.input_table[player_id][inp]=ord(msvcrt.getwch())
            self.display(player_id)
        return self

    def initbindinglinux(self):
        def main(stdscr):
            for player_id in range(2):
                for inp in range(4):
                    clear()
                    self.display(player_id)
                    self.input_table[player_id][inp]=stdscr.getch()
                self.display(player_id)
            return self

        if __name__ == '__main__':
            return curses.wrapper(main)

    def input_common(self, callback_queue):
        if is_win:
            input_user = self.inputs_windows()
        else:
            input_user = self.inputs_linux()

        if callback_queue is None: return input_user

        player_id = self.identify_player(input_user)

        if player_id is not None:
            result = (self.input_table[player_id].index(input_user), player_id)
            callback_queue.put(result) # Va mettre le resultat dans la queux a vote start_game_2v2
            return result
        return None


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
            # Accéder directement à json_data au lieu d'utiliser load()
            config_data = self.input_config.json_data

            # Prendre la première config si c'est une liste
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
                keyboard_keys = [122, 115, 113, 100]  # z, s, q, d
            else:
                keyboard_keys = [119, 115, 97, 100]   # w, s, a, d
            self.input_manager = InputManager([keyboard_keys, [105, 107, 106, 108]])
            self.menu_input_config = keyboard_keys

    def keyboard_settings_menu(self):
        """configutation des touches"""
        clear()

        joueur_temp = InputManager()

        if name == 'nt':
            for player_id in range(2):
                for inp in range(4):
                    clear()
                    print("=== Config des touches ===\n")
                    direction = ["HAUT", "BAS", "GAUCHE", "DROITE"][inp]
                    print(f"Joueur {player_id + 1} - Appuyez sur la touche pour {direction}")
                    joueur_temp.input_table[player_id][inp] = ord(msvcrt.getwch())
        else:
            pass # Linux on verra
        self.input_config.raw_save({"layout": joueur_temp.input_table})


        return joueur_temp

    def credits(self):
        clear()
        print(ASCIIART[1])
        if name == 'nt':
            msvcrt.getwch()
        else:
            def main(stdscr):
                stdscr.getch()
            curses.wrapper(main)

    def score(self):
        clear()
        save_manager = SaveManager()
        scores = save_manager.load()

        print(f"{COLOR['red']}=== Top 15 ===\n{COLOR['reset']}")

        liste = []
        for entry in scores:
            for nom, info in entry.items():
                liste.append([nom, info["score"], info["result"], info["date"]])

        for i in range(len(liste)):
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
                start_game_2v2(self.input_manager)

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

        colors_sample = sample(list(COLOR.keys())[:-1], k=4) # choisi 4 couleurs au hasard pour le menu SANS EN REPRENDRE 1 deja repris dans la liste
        self.selection_list = [
            f"{COLOR[colors_sample[0]]}Démarrer le jeu{COLOR['reset']}",
            f"{COLOR[colors_sample[1]]}Touches Clavier{COLOR['reset']}",
            f"{COLOR[colors_sample[2]]}Credits{COLOR['reset']}",
            f"{COLOR[colors_sample[3]]}Score{COLOR['reset']}"
        ]

    def refresh_menu(self, selected_index=0):
        """affiche le menu avec la selection actuelle"""
        clear()
        print(self.main_interface)
        for i in range(len(self.selection_list)):
            print(f"-[{'*' if selected_index == i else ' '}] {self.selection_list[i]}")

    def handle_menu_interaction(self, selected_index=0, menu_input_config=None):
        """
        gere tout ce qui est navigation dans le menu
        reuturn : l'optiuon selectionné
        """
        if name == 'nt':  # Windows
            while True:
                pinput = ord(msvcrt.getwch())

                # valider
                if pinput == menu_input_config[3]:  # Droite
                    return selected_index

                # aller en HAUT
                elif pinput == menu_input_config[0]:
                    selected_index = (selected_index - 1) % len(self.selection_list)

                # aller en BAS
                elif pinput == menu_input_config[1]:
                    selected_index = (selected_index + 1) % len(self.selection_list)

                self.refresh_menu(selected_index)

        else:  # Linux, dans la grande logique
            pass # on verra, on verra

def start_game_2v2(input_manager):
    """
    Docstring for start_game_2v2
    Cette fonction lance une partie de tron en 2v2

    :param input_manager: La classe qui va gerer tout ce bazar d'input
    Return rien du tout puisque c'est une boucle infinie qui se fini par un quit() méchant
    """
    player_blue = Player("O", "blue", CONFIG_SIZE_X // 2, 1)  # haut au centre
    player_orange = Player("O", "orange", CONFIG_SIZE_X // 2, CONFIG_SIZE_Y - 2)  # bas au centre

    board_instance = Board()

    board_instance.add_player(player_blue)
    board_instance.add_player(player_orange)

    callback_queue = queue.Queue() # Queue pour gerer la queue d'input

    # mapping des directions
    DIRECTION_MAP = {
        0: (0, -1),  # Haut
        1: (0, 1),   # Bas
        2: (-1, 0),  # Gauche
        3: (1, 0)    # Droite
    }
    board_instance.show_stadium()

    last_move_time = 0

    # Thread d'input qui tourne en permanence en arrière-plan
    def input_listener():
        """Thread qui écoute en continu les inputs clavier et les met dans la queue"""
        while True:
            input_manager.input_common(callback_queue)

    input_thread = threading.Thread(target=input_listener) # démarrer le thread d'écoute des inputs
    input_thread.start()

    while True:

        while not callback_queue.empty(): # traiter les inputs dispo
            try:
                # Recupere un msg sans attendre
                callback_message = callback_queue.get_nowait()

                direction, player_id = callback_message
                dx, dy = DIRECTION_MAP[direction]

                if player_id == 0:
                    player_blue.current_direction = (dx, dy)
                elif player_id == 1:
                    player_orange.current_direction = (dx, dy)

            except queue.Empty: # PLus d'input
                break

        current_time = time()
        if current_time - last_move_time >= 0.5: # Tout les 0.5 un peu pres refaire une image donc 2 fps

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


if not sys.stderr.isatty():
    system(f"start powershell.exe {sys.executable} {join(dirname(abspath(__file__)), 'tron_prof.py')}")
    winsound.PlaySound('tronost.wav', winsound.SND_FILENAME | winsound.SND_LOOP)
else:
    main()
