"""
▗▄▄▄   ▄▄▄      ▄▄▄▄   ▄▄▄     ■         ■  ▗▞▀▚▖ ▄▄▄  ■      ▄ ▄▄▄▄      ▗▞▀▚▖   ▐▌█  ▐▌▄▄▄▄  ▄   ▄    ■  ▐▌    ▄▄▄  ▄▄▄▄  
▐▌  █ █   █     █   █ █   █ ▗▄▟▙▄▖    ▗▄▟▙▄▖▐▛▀▀▘▀▄▄▗▄▟▙▄▖    ▄ █   █     ▐▛▀▀▘   ▐▌▀▄▄▞▘█   █ █   █ ▗▄▟▙▄▖▐▌   █   █ █   █ 
▐▌  █ ▀▄▄▄▀     █   █ ▀▄▄▄▀   ▐▌        ▐▌  ▝▚▄▄▖▄▄▄▀ ▐▌      █ █   █     ▝▚▄▄▖▗▞▀▜▌     █▄▄▄▀  ▀▀▀█   ▐▌  ▐▛▀▚▖▀▄▄▄▀ █   █ 
▐▙▄▄▀                         ▐▌        ▐▌            ▐▌      █                ▝▚▄▟▌     █     ▄   █   ▐▌  ▐▌ ▐▌            
                              ▐▌        ▐▌            ▐▌                                 ▀      ▀▀▀    ▐▌                                                                                                      

Arch & Renderaction - Tron game on console
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
    def __init__(self, symbol, color, x, y):
        self.symbol = symbol
        self.color = color
        self.x = x
        self.y = y
        self.previous_position = [self.get_position()]
        self.trace = "░"
        
        self.player_name = f"Player_{color}"
        self.score = 0
        self.winner = False
    
    def get_position(self): return self.y * CONFIG_REAL_SIZE + self.x
    
    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 1 <= new_x < CONFIG_REAL_SIZE - 1 and 1 <= new_y < CONFIG_SIZE - 1:
            self.previous_position.append(self.get_position())
            
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

class Board:
    def __init__(self, players=None):
        self.board = []
        self._create_board()
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

        self.board = [("#", "white")] * CONFIG_REAL_SIZE
        
        for i in range(CONFIG_SIZE - 2):
            self.board.append(("#", "white"))
            self.board += [(" ", "black")] * (CONFIG_REAL_SIZE - 2)
            self.board.append(("#", "white"))
        self.board += [("#", "white")] * CONFIG_REAL_SIZE
    
    def _check_collision(self):
        pos_collistion = []
        for player in self.players:
            for position in pos_collistion:
                if position == player.get_position() or position in player.previous_position:
                    player.winner = True
                    return True
            pos_collistion.append(player.get_position())
        return False

    def add_player(self, player): self.players.append(player)
    
    def show_stadium(self):
        system("clear")
        
        if self._check_collision():
            self.game_over()
            return

        for case in range(len(self.board)):
            char, color = self.board[case]
        
            for p in self.players: 
                if case in [pos for pos in p.previous_position]:
                    char, color = p.trace, p.color
                    break
            
            for player in self.players:
                if case == player.get_position():
                    char, color = player.symbol, player.color
                    break
                
            if (case + 1) % CONFIG_REAL_SIZE == 0:
                print(f"{COLOR[color]}{char}{COLOR['reset']}")
            else:
                print(f"{COLOR[color]}{char}{COLOR['reset']}", end="", flush=True)
                    

    def game_over(self):
        system("clear")
        
        print(f"{COLOR['white']}{self.GAME_OVER_SCREEN}{COLOR['reset']}")
        sleep(1)
        
        game_data = {}
        date = mktime(localtime())
        
        for player in self.players:
            if player.winner:
                player.score += 100
                print(f"{COLOR[player.color]}{player.player_name} WIN! Score: {player.score}{COLOR['reset']}")
                game_data[player.player_name] = {
                    "score": player.score,
                    "result": "win",
                    "mouvements": player.previous_position,
                    "date": date
                }
            else:
                print(f"{COLOR[player.color]}{player.player_name} LOSE! Score: {player.score}{COLOR['reset']}")
                game_data[player.player_name] = {
                    "score": player.score,
                    "result": "lose",
                    "mouvements": player.previous_position,
                    "date": date
                }
        
        self.save_manager.save(game_data)
        sleep(9)
        quit()

player_blue = Player("O", "blue", CONFIG_REAL_SIZE // 2, 1)
player_orange = Player("O", "orange", CONFIG_REAL_SIZE // 2, CONFIG_SIZE - 2)

board_instance = Board()
board_instance.add_player(player_blue)
board_instance.add_player(player_orange)
board_instance.show_stadium()


def test():
    player_orange.move_up()
    player_blue.move_down()
    board_instance.show_stadium()

def test1():
    player_blue.move_down()
    player_orange.move_left()
    board_instance.show_stadium()
    
for i in range(4):
    sleep(0.5)
    test()

for i in range(4):
    sleep(0.5)
    test1()