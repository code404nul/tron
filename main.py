# This is done without any external libraries, so colorama is not included. That can cause issues to display colors.
from os import get_terminal_size
from dataclasses import dataclass

COLOR  = {
    "black": "\033[31m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "white": "\033[37m",
    "reset": "\033[0m"
}

@dataclass
class config:
    size: int = 20
    factor: float = 1
    real_size: int = int(size * factor)

class board:
    def __init__(self):
        self.border_char = '#'
        self.show_color = "white" #change color here
    
    def show_staduim(self):
        print(f"{COLOR[self.show_color]}{self.border_char * config.real_size}{COLOR['reset']}")
        for i in range(config.real_size - config.factor):
            print(f"{COLOR[self.show_color]}{self.border_char}{COLOR['reset']}{' ' * int((config.size - 2) * config.factor + 2)}{COLOR[self.show_color]}{self.border_char}{COLOR['reset']}")
        print(f"{COLOR[self.show_color]}{self.border_char * config.real_size}{COLOR['reset']}")
        
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