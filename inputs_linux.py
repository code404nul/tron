import curses

def main(stdscr):
    stdscr.nodelay(1)
    while True:
        c = stdscr.getch()
        if c != -1:
            stdscr.addstr(str(c) + ' ')
            stdscr.refresh()
            stdscr.move(0, 0)
        

if __name__ == '__main__':
    curses.wrapper(main)
