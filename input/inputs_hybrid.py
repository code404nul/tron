import os

class Input_gestion():

    def __init__(self,tab=[95,95,95,95]):
        self.input_table=tab

    def __str__(self):
        return "UP:"+chr(self.input_table[0])+"\n"+"DOWN:"+chr(self.input_table[1])+"\n"+"LEFT:"+chr(self.input_table[2])+"\n"+"RIGHT:"+chr(self.input_table[3])

    def inputs_windows(self):
        clear = lambda: os.system('cls')
        import msvcrt
        while True:
            clear()
            pinput=ord(msvcrt.getwch())

    def initbinding(self):
        clear = lambda: os.system('cls')
        for inp in range(4):
            clear()
            print(self)
            self.input_table[inp]=ord(msvcrt.getwch())
        print(self)
    
    def initbinding2(self):
        clear = lambda: os.system('clear')
        import curses
        def main(stdscr):
            for inp in range(4):
                clear()
                print(self)
                self.input_table[inp]=stdscr.getch()
            print(self)

        if __name__ == '__main__':
            curses.wrapper(main)
        
    def inputs_linux(self):
        clear = lambda: os.system('clear')
        import curses

        def main(stdscr,self=self):
            while True:
                pinput = stdscr.getch()
                clear()
                print(pinput)

        if __name__ == '__main__':
            curses.wrapper(main)


#player1=Input_gestion()

#if os.name == 'nt':
#    player1.initbinding()
#    player1.inputs_windows()
#else:
#    player1.initbinding2()
#    player1.inputs_linux()


