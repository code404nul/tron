#1. Lancer le jeux
#- demander le nom des joueur et le nombre de joeur
#2. REMAP de touche
#3. Credit et info sur la config (jourbnal de botrfd)


def execution_menu():
    print("""
  _____ ___  ___  _  _               _   _                       _ _ _   _          
 |_   _| _ \/ _ \| \| |    _ __ _  _| |_| |_  ___ _ _     ___ __| (_) |_(_)___ _ _  
   | | |   / (_) | .` |   | '_ \ || |  _| ' \/ _ \ ' \   / -_) _` | |  _| / _ \ ' \ 
   |_| |_|_\\\___/|_|\_|   | .__/\_, |\__|_||_\___/_||_|  \___\__,_|_|\__|_\___/_||_|
                          |_|   |__/                                                
                                           
        1.START GAME
        2.CONTROLS
        3.CREDIT AND MORE
""")
    selection=input("")
    if selection==1:
        pass
    elif selection==2:
        pass
    elif selection==3:
        pass
    else:
        execution_menu()
    

execution_menu()