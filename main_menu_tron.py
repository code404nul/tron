#1. Lancer le jeux
#- demander le nom des joueur et le nombre de joeur
#2. REMAP de touche
#3. Credit et info sur la config (jourbnal de botrfd)

import os

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

def execution_menu(joueur=[Input_gestion([122,115,113,100]),Input_gestion([259,258,260,261])]):
    clear()
    print("""
  _______                              _   _                            _ _ _   _
 |__   __|                            | | | |                          | (_) | (_)
    | |_ __ ___  _ __      _ __  _   _| |_| |__   ___  _ __     ___  __| |_| |_ _  ___  _ __
    | | '__/ _ \| '_ \    | '_ \| | | | __| '_ \ / _ \| '_ \   / _ \/ _` | | __| |/ _ \| '_ \
    | | | | (_) | | | |   | |_) | |_| | |_| | | | (_) | | | | |  __/ (_| | | |_| | (_) | | | |
    |_|_|  \___/|_| |_|   | .__/ \__, |\__|_| |_|\___/|_| |_|  \___|\__,_|_|\__|_|\___/|_| |_|
                          | |     __/ |
                          |_|    |___/
        1.START GAME
        2.CONTROLS
        3.CREDIT AND MORE
""")
    try:
        selection=int(input())
    except ValueError:
        execution_menu(joueur)

    if selection==1:
        start_game()

    elif selection==2:

        joueur = [Input_gestion(), Input_gestion()]
        if os.name == 'nt':
            joueur[0].initbindingwin()
            joueur[1].initbindingwin()
            execution_menu(joueur)
        else:
            joueur[0].initbindinglinux()
            joueur[1].initbindinglinux()
            execution_menu(joueur)


    elif selection==3:
        ink=input()
        print(str(joueur[ink].input_table))

    else:
        execution_menu(joueur)


execution_menu()
