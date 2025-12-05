#1. Lancer le jeux
#- demander le nom des joueur et le nombre de joeur
#2. REMAP de touche
#3. Credit et info sur la config (jourbnal de botrfd)   C:\EduPython\App\python.exe C:\Users\bmich\Downloads\test.py     C:\EduPython\App\python.exe \\ZEUS\bryan.monnin$\Downloads\htehtres.py

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

clear= lambda: system('cls' if name=='nt' else 'clear')

class Input_gestion():

    def __init__(self,tab=[95,95,95,95]):
        self.input_table=tab

    def __str__(self):
        return f"""
UP:{chr(self.input_table[0])}
DOWN:{chr(self.input_table[1])}
LEFT:{chr(self.input_table[2])}
RIGHT:{chr(self.input_table[3])}
"""

    def inputs_windows(self):
        while True:
            pinput=ord(msvcrt.getwch())
            # return pinput ?

    def inputs_linux(self):

        def main(stdscr,self=self):
            while True:
                pinput = stdscr.getch() # Pourquoi clear? si on l'uilise dans le jeu tout ca se supprimer?
                print(pinput)

        return curses.wrapper(main) # ? Il faut les retourner un jour...

    def initbindingwin(self):
        for inp in range(4):
            clear()
            print(self)
            self.input_table[inp]=ord(msvcrt.getwch())
        print(self)
        return self

    def initbindinglinux(self):
        def main(stdscr):
            for inp in range(4):
                clear()
                print(self)
                self.input_table[inp]=stdscr.getch()
            print(self)
            return self

        if __name__ == '__main__':
            curses.wrapper(main)


joueur=[Input_gestion([122,115,113,100]),Input_gestion([259,258,260,261])]

asciiart=[r"""
 ███████████
▒█▒▒▒███▒▒▒█
▒   ▒███  ▒  ████████   ██████  ████████
    ▒███    ▒▒███▒▒███ ███▒▒███▒▒███▒▒███
    ▒███     ▒███ ▒▒▒ ▒███ ▒███ ▒███ ▒███
    ▒███     ▒███     ▒███ ▒███ ▒███ ▒███
    █████    █████    ▒▒██████  ████ █████
   ▒▒▒▒▒    ▒▒▒▒▒      ▒▒▒▒▒▒  ▒▒▒▒ ▒▒▒▒▒ """,r"""
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
"""]

def score(): pass

def demmarer_le_jeu(): pass

def menu_touches_clavier():
    joueur=[Input_gestion(),Input_gestion()]
    if name == 'nt':
        joueur[0].initbindingwin()
        joueur[1].initbindingwin()
    else:
        joueur[0].initbindinglinux()
        joueur[1].initbindinglinux()
    return joueur

class Menu:

    def __init__(self,tron_ascii=asciiart[0]):
        self.main_interface=tron_ascii
        self.liste_des_selections=["Demmarer le jeu","Touches Clavier","Credits","Score"]

    def refresh_menu(self,placement=0):
        clear()
        print(self.main_interface)
        for i in range(len(self.liste_des_selections)):
            print(f"-[{'*' if placement == i else ' '}] {self.liste_des_selections[i]}")


    def lancer_interaction_avec_menu(self):
        placement = 0
        if name == 'nt':
            while True:
                pinput = ord(msvcrt.getwch())
                if pinput == 100: break
                elif pinput == 122 and placement != 0: placement += -1
                elif pinput == 115 and placement < len(self.liste_des_selections)-1: placement += 1
                self.refresh_menu(placement)
            return placement
        else:
            def main(stdscr,placement=placement,self=self):
                while True:
                    pinput = stdscr.getch()
                    if pinput == 100: break
                    elif pinput == 122 and placement > 0: placement += -1
                    elif pinput == 115 and placement < len(self.liste_des_selections)-1: placement += 1
                    self.refresh_menu(placement)
                return placement

            return curses.wrapper(main)



menu=Menu()
while True:
    menu_selectionne = menu.lancer_interaction_avec_menu()
    if menu_selectionne == 0:
        break
    if menu_selectionne == 1:
        joueur = menu_touches_clavier()
        break

print(joueur[0])
print(joueur[1])

 #with open(filename, "r") as f: