#1. Lancer le jeux
#- demander le nom des joueur et le nombre de joeur
#2. REMAP de touche
#3. Credit et info sur la config (jourbnal de botrfd)

import os
from copy import deepcopy

if os.name == 'nt': import msvcrt
else: import curses

clear= lambda: os.system('cls' if os.name=='nt' else 'clear')

class Input_gestion():

    def __init__(self,tab=[95,95,95,95]):
        self.input_table=tab

    def __str__(self):
        return "UP:"+chr(self.input_table[0])+"\n"+"DOWN:"+chr(self.input_table[1])+"\n"+"LEFT:"+chr(self.input_table[2])+"\n"+"RIGHT:"+chr(self.input_table[3])

    def inputs_windows(self):
        while True:
            clear()
            pinput=ord(msvcrt.getwch())

    def initbindingwin(self):
        for inp in range(4):
            clear()
            print(self)
            self.input_table[inp]=ord(msvcrt.getwch())
        print(self)

    def initbindinglinux(self):
        def main(stdscr):
            for inp in range(4):
                clear()
                print(self)
                self.input_table[inp]=stdscr.getch()
            print(self)

        if __name__ == '__main__':
            curses.wrapper(main)

    def inputs_linux(self):

        def main(stdscr,self=self):
            while True:
                pinput = stdscr.getch()
                clear()
                print(pinput)

        if __name__ == '__main__':
            curses.wrapper(main)


def start_game():
    print("t'as crue le jeu il est fini?")

joueur=[Input_gestion([122,115,113,100]),Input_gestion([259,258,260,261])]


class menu:
    def __init__(self):
        print("""
 _______ ______ _______ _______ 
(_______|_____ (_______|_______)
    _    _____) )     _ _     _ 
   | |  |  __  / |   | | |   | |
   | |  | |  \ \ |___| | |   | |
   |_|  |_|   |_\_____/|_|   |_|""")
        self.menu_count = 0
        self.menu = {}
        
    def create_selection(self, menu_name, fonction):
        self.menu_count += 1
        self.menu[menu_name] = [deepcopy(self.menu_count), " ", fonction]
        print(f"     [{self.pointer[self.menu_count]}] - {menu_name}")


    def input_binding(self):

        joueur = [Input_gestion(), Input_gestion()]
        if os.name == 'nt':
            joueur[0].initbindingwin()
            joueur[1].initbindingwin()
            execution_menu(joueur)
        else:
            joueur[0].initbindinglinux()
            joueur[1].initbindinglinux()
            execution_menu(joueur)

execution_menu()
