#C:\EduPython\App\python.exe \\ZEUS\bryan.monnin$\Downloads\htehtres.py

import msvcrt
import os

clear = lambda: os.system('cls')

class Inputbinding():
    def __init__(self,tab=[95,95,95,95]):
        self.up=tab[0]
        self.down=tab[1]
        self.left=tab[2]
        self.right=tab[3]

    def __str__(self):
        return "UP:"+chr(self.up)+"\n"+"DOWN:"+chr(self.down)+"\n"+"LEFT:"+chr(self.left)+"\n"+"RIGHT:"+chr(self.right)


def initbinding(playersinput=Inputbinding()):
    clear()
    print(playersinput)
    playersinput.up=ord(msvcrt.getwch())
    clear()
    print(playersinput)
    playersinput.down=ord(msvcrt.getwch())
    clear()
    print(playersinput)
    playersinput.left=ord(msvcrt.getwch())
    clear()
    print(playersinput)
    playersinput.right=ord(msvcrt.getwch())
    clear()
    print(playersinput)
    return playersinput

initbinding()



#while True:
#    print(ord(msvcrt.getwch()))
