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
from os import name, system # récuperer le nom de l'os ('nt' sur windows et 'posix' sur linux) et permettre l'execution de system('cls')
import threading # Gerer l'execution de fonction en parrallèle.
if name == 'nt': import msvcrt #msvcrt est une librairie interne qui permet de lire les inputs du clavier
else: import curses #similaire à msvcrt mais pour linux

clear= lambda: system('cls' if name == 'nt' else 'clear') #pour éviter d'écrire system('cls') à chaque fois, on va écrire clear()

system('cls')

class Input_gestion(): #creation d'une class inputgestion pour stocker les controles des deux joueurs et gerer tout ce qui touche a la detection d'entree clavier

    def __init__(self,tab = None): #les controles des joueurs sont stocker dans une matrice tab de 2x4 pour les 2 joueurs et les 4 touches haut bas gauche droite
        if tab: self.input_table=tab #si tab existe alors self.inputtable prend la valeur de tab
        else: self.input_table = [[95,95,95,95],[95,95,95,95]] #sinon alors self.inputtable devient une matrice remplie de 95 qui correspond en ascii au '_'

    def afficher(self,idjoueur = 3): #une fonction qui affiche de manière esthetique les inputs des joueur
        if idjoueur > 2 or idjoueur < 0: #si l'id du joueur dont on veut print les touches est mal précisé alors la fonction print les touches des 2 joueurs
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
Joueur {'1' if idjoueur == 0 else '2'}
UP:{chr(self.input_table[idjoueur][0])}
DOWN:{chr(self.input_table[idjoueur][1])}
LEFT:{chr(self.input_table[idjoueur][2])}
RIGHT:{chr(self.input_table[idjoueur][3])}
""")


    def inputs_windows(self): #cette fonction return la touche pressé sous forme decimal en ascii(ex: si 'z' est pressé alors ça return 122)
        return ord(msvcrt.getwch())


    def inputs_linux(self): #cette fonction fait pareil que inputs_windows() mais en utilisant curses pour linux

        def main(stdscr,self=self):
            while True:
                pinput = stdscr.getch() # Pourquoi clear? si on l'uilise dans le jeu tout ca se supprimer?
                print(pinput)

        return curses.wrapper(main) # ? Il faut les retourner un jour...

    def initbindingwin(self):
        for idjoueur in range(2):
            for inp in range(4):
                clear()
                self.afficher(idjoueur)
                self.input_table[idjoueur][inp]=ord(msvcrt.getwch())
            self.afficher(idjoueur)
        return self

    def initbindinglinux(self):
        def main(stdscr):
            for idjoueur in range(2):
                for inp in range(4):
                    clear()
                    self.afficher(idjoueur)
                    self.input_table[idjoueur][inp]=stdscr.getch()
                self.afficher(idjoueur)
            return self

        if __name__ == '__main__':
            return curses.wrapper(main)

disposition=input("""
1. AZERTY?
2. QWERTY?
""")
if int(disposition) == 1: disposition_du_clavier = [122,115,113,100]
else: disposition_du_clavier = [119,115,97,100]
joueur=Input_gestion([disposition_du_clavier,[105,107,106,108]])
input_pour_le_menu=disposition_du_clavier



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

def score(): print(574657486464)

def demmarer_le_jeu(): pass

def menu_touches_clavier():
    joueur=Input_gestion()
    if name == 'nt':
        joueur.initbindingwin()
    else:
        joueur.initbindinglinux()
    return joueur

def credits():
    clear()
    print(asciiart[1])
    if name == 'nt': msvcrt.getwch()
    else:
        def main(stdscr):
            stdscr.getch()
        curses.wrapper(main)

class Menu:

    def __init__(self,tron_ascii=asciiart[0]):
        self.main_interface=tron_ascii
        self.liste_des_selections=["Demmarer le jeu","Touches Clavier","Credits","Score"]

    def refresh_menu(self,placement=0):
        clear()
        print(self.main_interface)
        for i in range(len(self.liste_des_selections)):
            print(f"-[{'*' if placement == i else ' '}] {self.liste_des_selections[i]}")


    def lancer_interaction_avec_menu(self,placement=0):
        if name == 'nt':
            while True:
                pinput = ord(msvcrt.getwch())
                if pinput == input_pour_le_menu[3]: break
                elif pinput == input_pour_le_menu[0] and placement != 0: placement += -1
                elif pinput == input_pour_le_menu[1] and placement < len(self.liste_des_selections)-1: placement += 1
                elif pinput == input_pour_le_menu[0] and not(placement != 0): placement = len(self.liste_des_selections)-1
                elif pinput == input_pour_le_menu[1] and not(placement < len(self.liste_des_selections)-1): placement = 0
                self.refresh_menu(placement)
            return placement
        else:
            def main(stdscr,placement=placement,self=self):
                while True:
                    pinput = stdscr.getch()
                    if pinput == input_pour_le_menu[3]: break
                    elif pinput == input_pour_le_menu[0] and placement > 0: placement += -1
                    elif pinput == input_pour_le_menu[1] and placement < len(self.liste_des_selections)-1: placement += 1
                    self.refresh_menu(placement)
                return placement

            return curses.wrapper(main)



menu=Menu()
def lancer_menu_principal(menu=menu,joueur=joueur,menu_selectionne=0):
    menu.refresh_menu(menu_selectionne)
    while True:
        menu_selectionne = menu.lancer_interaction_avec_menu(menu_selectionne)
        if menu_selectionne == 0:
            return (joueur,1,menu_selectionne)
        if menu_selectionne == 1:
            joueur = menu_touches_clavier()
            return (joueur,0,menu_selectionne)
        if menu_selectionne == 2:
            credits()
            return (joueur,0,menu_selectionne)
        if menu_selectionne == 3:
            score()
            return (joueur,0,menu_selectionne)

def verifier_si_il_faut_lancer_le_jeu(menu=menu,joueur=joueur):
    sortie = lancer_menu_principal(menu,joueur)
    if sortie[1]: return sortie[0]
    while True:
        sortie = lancer_menu_principal(menu,sortie[0],sortie[2])
        if sortie[1]: return sortie[0]

joueur=verifier_si_il_faut_lancer_le_jeu()

joueur.afficher()

demmarer_le_jeu()

print(name)

 #with open(filename, "r") as f: