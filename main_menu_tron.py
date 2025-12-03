#1. Lancer le jeux
#- demander le nom des joueur et le nombre de joeur
#2. REMAP de touche
#3. Credit et info sur la config (jourbnal de botrfd)

"""
--------- IMPORTANT -----------
Render TODO, fait un systeme de gestion input

Fait un meilleur systeme ou tes inputs se retourne vraiment 
En gros dans tes inputs bindung utiliser des fonction inputs
De plus, fait un systeme de boucle infini (mais on doit pouvoir acceder au input a l'exterieur de la fonction stp), ou chaque joueur appue sur une touche les uns après les autres...
Tu peux gerer tout le reste après c'est pas la prio.

"""

from copy import deepcopy
from os import name, system
import threading # Gerer l'execution de fonction en parrallèle. 
if name == 'nt': import msvcrt
else: import curses

if name == 'nt': import msvcrt
else: import curses

clear= lambda: system('cls' if name=='nt' else 'clear')

class Input_gestion():

    def __init__(self,tab=[95,95,95,95]):
        self.input_table=tab

    def __str__(self):
        return "UP:"+chr(self.input_table[0])+"\n"+"DOWN:"+chr(self.input_table[1])+"\n"+"LEFT:"+chr(self.input_table[2])+"\n"+"RIGHT:"+chr(self.input_table[3])

    def inputs_windows(self):
        while True:
            system("clear")
            pinput=ord(msvcrt.getwch())
            # return pinput ?

    def inputs_linux(self):

        def main(stdscr,self=self):
            while True:
                pinput = stdscr.getch() # Pourquoi clear? si on l'uilise dans le jeu tout ca se supprimer?
                return pinput

        return curses.wrapper(main) # ? Il faut les retourner un jour...

    def initbindingwin(self):
        for inp in range(4):
            system("clear")
            print(self)
            self.input_table[inp]=ord(msvcrt.getwch())
        print(self)

    def initbindinglinux(self):
        def main(stdscr):
            for inp in range(4):
                system("clear")
                print(self)
                self.input_table[inp]=stdscr.getch()
            print(self)

        if __name__ == '__main__':
            curses.wrapper(main)


joueur=[Input_gestion([122,115,113,100]),Input_gestion([259,258,260,261])]


class Menu:
    def __init__(self):
        print("""
 _______ ______ _______ _______ 
(_______|_____ (_______|_______)
    _    _____) )     _ _     _ 
   | |  |  __  / |   | | |   | |
   | |  | |  \ \ |___| | |   | |
   |_|  |_|   |_\_____/|_|   |_|\n""")
        self.menu_count = 0
        self.menu = {}
        self.pointer = []
        
    def create_selection(self, menu_name, fonction):
        self.menu_count += 1
        self.menu[menu_name] = [deepcopy(self.menu_count), "*", fonction]
        self.pointer.append(" ")
        print(f"     [{self.pointer[self.menu[menu_name][0] - 1]}] - {menu_name}")

    def input_binding(self):

        joueur = [Input_gestion(), Input_gestion()]
        if name == 'nt': # TODO
            joueur[0].initbindingwin()
            joueur[1].initbindingwin()
        else:
            joueur[0].initbindinglinux()
            joueur[1].initbindinglinux()
        
    def credit(self):
        system("clear")
        print("""
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
""")

"""
menu = Menu()
menu.create_selection("Input Binding", menu.input_binding)
menu.create_selection("Start Game", start_game)
menu.create_selection("credit", menu.credit)


input = Input_gestion()
print(input.inputs_linux())
"""
