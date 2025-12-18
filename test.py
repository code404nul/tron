"""Gestionnaire d'entrées clavier simple pour 2 joueurs."""
from os import name
if name == "nt":
    IS_WIN = True
    import msvcrt
else:
    IS_WIN = False
    import curses
    
    
class Input_gestion():
    def __init__(self, tab=None):
        if tab: 
            self.input_table = tab
        else: 
            self.input_table = [[122, 115, 113, 100], [95, 95, 95, 95]]
        self.stdscr = None  # Pour stocker l'écran curses
    
    def afficher(self, idjoueur=3):
        if idjoueur > 2 or idjoueur < 0:
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
""")
        else:
            print(f"""
Joueur {'1' if idjoueur == 0 else '2'}
UP:{chr(self.input_table[idjoueur][0])}
DOWN:{chr(self.input_table[idjoueur][1])}
LEFT:{chr(self.input_table[idjoueur][2])}
RIGHT:{chr(self.input_table[idjoueur][3])}
""")
    
    def identify_player(self, input_user):
        for i in range(2):
            if input_user in self.input_table[i]:
                return i
        return None
    
    def inputs_windows(self):
        return ord(msvcrt.getwch())
    
    def inputs_linux(self):
        curses.cbreak()
        return self.stdscr.getch()
    
    def input_common(self):
        if IS_WIN: 
            input_user = self.inputs_windows()
        else: 
            input_user = self.inputs_linux()
        player_id = self.identify_player(input_user)
        
        if player_id is not None: return (self.input_table[player_id].index(input_user), player_id)
        return input_user
    
    def print_curses(self, text):
        """Affiche du texte pour que notre ami curses soit content"""
        if IS_WIN:
            print(text)
        else:
            self.stdscr.addstr(text + "\n")
            self.stdscr.refresh()
    
    def clear_screen(self):
        """efface le texte de l'ecran"""
        if IS_WIN:
            from os import system
            system("cls")
        else:
            # Des probleme avec curses et linux et le screen
            self.stdscr.clear()
            self.stdscr.refresh()
    
    def initbinding(self):
        self.input_table = [[], []]
        
        for joueur in range(2):
            for keys in ["HAUT", "BAS", "GAUCHE", "DROITE"]:
                self.clear_screen()
                self.print_curses(f"--- Joueur {joueur + 1} ---")
                self.print_curses(f"Pour : {keys}")
                self.print_curses("Appuyez sur une touche...")
                
                key = self.input_common()
                
                self.print_curses(f"Clé {key} validée !")
                self.input_table[joueur].append(key)
        
        self.clear_screen()
        self.print_curses(f"Config finito{", massacrer votre clavier (a l'aide de votre calvisie) et attendez" if not IS_WIN else ""}")
        return
    
    def run_with_curses(self):
        """Regler 2/3 trucs avec curses pour inputbuiding et linux entre bonhommme"""
        def main(stdscr):
            self.stdscr = stdscr
            self.stdscr.nodelay(False)  # bloaquant
            curses.cbreak() # pour la touche maitenant oublie le enter
            self.stdscr.keypad(True) # Les fleches et les trucs bizzar que on oublie aussi ^^
            
            self.initbinding()
            
            result = self.input_common()
            self.print_curses("FIni?")
            return result
        
        return curses.wrapper(main)
    
    def buinding(self):
        """principal point d'entré"""
        if IS_WIN: self.initbinding()
        else: self.run_with_curses()


# Utilisation
input_config = Input_gestion()
input_config.buinding()
while True:
    print(input_config.input_common())