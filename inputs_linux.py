import curses

class Inputbinding():
    def __init__(self,tab=[95,95,95,95]):
        self.up=tab[0]
        self.down=tab[1]
        self.left=tab[2]
        self.right=tab[3]

    def __str__(self):
        return "UP:"+chr(self.up)+"\n"+"DOWN:"+chr(self.down)+"\n"+"LEFT:"+chr(self.left)+"\n"+"RIGHT:"+chr(self.right)


def main(stdscr):

    playersinput=Inputbinding()
    print(playersinput)
    playersinput.up=stdscr.getch()
    print(playersinput)
    playersinput.down=stdscr.getch()
    print(playersinput)
    playersinput.left=stdscr.getch()
    print(playersinput)
    playersinput.right=stdscr.getch()
    print(playersinput)


    stdscr.nodelay(1)
    while True:
        c = stdscr.getch()
        if c != -1:
            pinput=c
            print(pinput)
            

def initbinding(playersinput=Inputbinding()):
    
    return playersinput


        
if __name__ == '__main__':
    curses.wrapper(main)

#stdscr.addstr(str(c) + ' ') print et clear la console