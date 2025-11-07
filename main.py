# This is done without any external libraries, so colorama is not included. That can cause issues to display colors.
from os import get_terminal_size

COLOR  = {
    "black": "\033[31m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "white": "\033[37m",
    "reset": "\033[0m"
}

CONFIG_SIZE: int = get_terminal_size().lines - 5
CONFIG_FACTOR: int = 2
CONFIG_REAL_SIZE: int = CONFIG_SIZE * CONFIG_FACTOR

class board:
    def __init__(self):

        self.border_char = '#'
        self.show_color = "white" #change color here
    
    def show_staduim(self):
        print(f"{COLOR[self.show_color]}{self.border_char * CONFIG_REAL_SIZE}{COLOR['reset']}")
        for i in range(CONFIG_SIZE - 2):
            print(f"{COLOR[self.show_color]}{self.border_char}{COLOR['reset']}{' ' * ((CONFIG_SIZE - 2) * CONFIG_FACTOR + 2)}{COLOR[self.show_color]}{self.border_char}{COLOR['reset']}")
        print(f"{COLOR[self.show_color]}{self.border_char * CONFIG_REAL_SIZE}{COLOR['reset']}")
        
class player:
    def __init__(self, color, name, position):
        self.color = color
        self.name = name
        self.position = position
        self.velocity = 20
        
    def show_on_screen(self):
        pass
    
area = board()
area.show_staduim()