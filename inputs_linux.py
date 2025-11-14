import curses

def main(stdscr):
    stdscr.nodelay(1)
    while True:
        c = stdscr.getch()
        if c != -1:
            stdscr.addstr(str(c) + ' ')
            pinput=c
            break
    print("jehfiesfhuyesfiufgqeztyfqgzyt-")
    return pinput
        

if __name__ == '__main__':
    curses.wrapper(main)
