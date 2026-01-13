from os import system
import sys
from os.path import abspath, dirname, join
import subprocess


system(f"start powershell.exe {sys.executable} {join(dirname(abspath(__file__)), 'tron_prof.py')}")
if not (input("Cela a t'il fonctionner ? (Y/n) (O/n)").lower() in ["", "y", "o"]):
    subprocess.Popen(["powershell.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)