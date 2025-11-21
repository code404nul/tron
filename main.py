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

from os import get_terminal_size, system, path
from time import sleep, mktime, localtime, ctime # ctime for convert sec to date str
import json

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

CONFIG_SIZE: int = get_terminal_size().lines - 5
CONFIG_FACTOR: int = 2
CONFIG_REAL_SIZE: int = CONFIG_SIZE * CONFIG_FACTOR

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

class Player:
    def __init__(self, symbol, color, x, y, player_name=None):
        self.symbol = symbol
        self.color = color
        self.x = x
        self.y = y
        self.previous_position = [self.get_pos()]
        self.trace = "░"
        
        self.player_name = player_name if player_name else f"Player_{color}"
        self.score = 0
        self.loser = False
    
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
            return True
        return False
    
    def move_left(self): return self.move(-1, 0)
    def move_right(self): return self.move(1, 0)
    def move_up(self):  return self.move(0, -1)
    def move_down(self): return self.move(0, 1)
    
    def render(self): return f"{COLOR[self.color]}{self.symbol}{COLOR['reset']}"

class Player_AI(Player):
    def __init__(self, symbol, color, x, y, board, player_name=None):
        super().__init__(symbol, color, x, y, player_name)
        
        self.board = board
        self.other_players = []
        for player in board.players:
            if type(player) == Player:
                self.other_players.append(player)
        
        
        self.avoid_list = [i for i in range(len(board.board)) if board.board[i][0] == "#"]
    
    def _avoid_case(self):
        for player in self.other_players: self.avoid_list += list(set(player.previous_position))

    def detect_possibility(self, case):
        ENTRYS = {case-1 : self.move_left, 
                        case+1 : self.move_right,
                        case-CONFIG_REAL_SIZE : self.move_up, 
                        case+CONFIG_REAL_SIZE : self.move_down}
        self._avoid_case()

        possibilitys = []
        for possibility in ENTRYS.values():
            if not (possibility in self.avoid_list):
                possibilitys.append(possibility)
        return possibility
    
    def test(self):
        return self.detect_possibility(self.get_pos())
    

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
        
        #Ligne des cotées
        for i in range(CONFIG_SIZE - 2):
            self.board.append(("#", "white"))
            self.board += [(" ", "black")] * (CONFIG_REAL_SIZE - 2)
            self.board.append(("#", "white"))
            
        self.board += [("#", "white")] * CONFIG_REAL_SIZE #Bord du dessous
    
    def _check_collision(self):
        for player in self.players:
            
            previous_pos = player.previous_position[1:] # Fix biscornu de position inital qui arrive 2 fois
            print(previous_pos)
            
            if (len(previous_pos) != len(set(previous_pos))) and len(previous_pos) > 3: # Verifie si dans les positions y a 2 fois la meme, et verifie si y a eu moins 3 valeur, toujours le fix biscornu et puis ca sera une feature si le joeur meurt des le debut, ca fonctionne comme ca on touche pas !
                player.loser = True
                return True
            
            for other_player in self.players: #peut etre utile pour du +2 joeurs
                if other_player.player_name != player.player_name:
                    if player.previous_position[-1] in other_player.previous_position: #Si la pos actuelle et dans la pos d'un autre joueur 
                        player.loser = True
                        return True
        
        return False

    def _game_over(self):
        sleep(1)
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
        system("clear")
        
        if self._check_collision():
            print("exec game over")
            self._game_over()
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

player_blue = Player("O", "blue", CONFIG_REAL_SIZE // 2, 1)

board_instance = Board()
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