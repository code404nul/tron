from os import system, path, get_terminal_size #Pour l'interaction ordi-utilisateur, on va souvent utiliser system pour "clear" la console
from math import exp #Preatique pour l'exp
from random import uniform, gauss, choice, randint #Pour tout les choix aléatoire
from copy import deepcopy #Pour copier une instance, en changeant sont adresse mémoire
from time import sleep, mktime, localtime, ctime # ctime sec (timestamp) -> str #Gestion du temps
import json # Gestion fichier .json, utile pour sauvegarde, lecture
import threading

# Variable globale pour contrôler l'arrêt
stop_flag = False

def ae():
    """Votre fonction - vérifiez juste stop_flag dans vos boucles"""
    global stop_flag
    WIDTH = get_terminal_size()[0] - 1
    DELAY = 0.04

    steps_before_switch = 20

    BLOCK_CHAR = '#'
    BLOCK_WIDTH = 14

    empty_chars = list('~                                          ')

    pos = 0
    speed = 0
    step = 0
    total_steps = 0
    direction = 'right'
    while not stop_flag:
        if step > steps_before_switch and direction == 'right':
            speed += 1
            pos += speed
            if pos > WIDTH - BLOCK_WIDTH:
                pos = WIDTH - BLOCK_WIDTH
                step = 0
                speed = 0
                direction = 'left'
                steps_before_switch = randint(10, 40)  # was 20, 70
                if len(empty_chars) > 4:
                    empty_chars.pop()
                    empty_chars.pop()
                    empty_chars.pop()
        elif step > steps_before_switch and direction == 'left':
            speed -= 1
            pos += speed
            if pos < 0:
                pos = 0
                step = 0
                speed = 0
                direction = 'right'
                steps_before_switch = randint(1, 20)   # was 10, 40
                if len(empty_chars) > 4:
                    empty_chars.pop()
                    empty_chars.pop()
                    empty_chars.pop()

        for i in range(BLOCK_WIDTH // 2):
            columns = [choice(empty_chars) for i in range(WIDTH)]
            for i in range(pos, pos + BLOCK_WIDTH):
                columns[i] = BLOCK_CHAR
            print(''.join(columns))
        sleep(DELAY)
        
        step += 1
        total_steps += 1
        if total_steps == 1000:
            total_steps = 0
            empty_chars = list('~                                          ')


# Démarrer le thread
def demarrer():
    global stop_flag
    stop_flag = False
    thread = threading.Thread(target=ae)
    thread.start()
    return thread

# Arrêter le thread
def arreter():
    global stop_flag
    stop_flag = True


# Exemple d'utilisation
if __name__ == "__main__":
    # Démarrer
    t = demarrer()
    
    # Laisser tourner 5 secondes
    sleep(5)
    
    # Arrêter
    arreter()
    t.join()  # Attendre la fin
    
    print("Terminé")