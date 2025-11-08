from os import get_terminal_size, system
from time import sleep

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

class Player:
    def __init__(self, symbol, color, x, y):
        self.symbol = symbol
        self.color = color
        self.x = x
        self.y = y
    
    def get_position(self): return self.y * CONFIG_REAL_SIZE + self.x
    
    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 1 <= new_x < CONFIG_REAL_SIZE - 1 and 1 <= new_y < CONFIG_SIZE - 1:
            self.x = new_x
            self.y = new_y
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
    
    def _create_board(self): #fonction privée

        self.board = [("#", "white")] * CONFIG_REAL_SIZE
        
        for i in range(CONFIG_SIZE - 2):
            self.board.append(("#", "white"))
            self.board += [(" ", "black")] * (CONFIG_REAL_SIZE - 2)
            self.board.append(("#", "white"))
        self.board += [("#", "white")] * CONFIG_REAL_SIZE
    
    def add_player(self, player): self.players.append(player)
    
    def show_stadium(self):
        system("clear")
        
        for case in range(len(self.board)):
            player_at_pos = None
            for player in self.players:
                if case == player.get_position():
                    player_at_pos = player
                    break
            
            if player_at_pos:
                print(player_at_pos.render(), end="" if (case + 1) % CONFIG_REAL_SIZE != 0 else "\n", flush=True)
            else:
                char, color = self.board[case]
                if (case + 1) % CONFIG_REAL_SIZE == 0:
                    print(f"{COLOR[color]}{char}{COLOR['reset']}")
                else:
                    print(f"{COLOR[color]}{char}{COLOR['reset']}", end="", flush=True)

player_blue = Player("O", "blue", CONFIG_REAL_SIZE // 2, 1)
player_orange = Player("O", "orange", CONFIG_REAL_SIZE // 2, CONFIG_SIZE - 2)

board_instance = Board()
board_instance.add_player(player_blue)
board_instance.add_player(player_orange)
board_instance.show_stadium()

def test():
    player_blue.move_down()
    player_orange.move_up()
    board_instance.show_stadium()
    
for i in range(40):
    sleep(0.03)
    test()