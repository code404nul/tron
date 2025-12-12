# Créé par jules.henriotcolin, le 11/12/2025 en Python 3.7

import os

is_on_edupython = False
try:
    import lycee
    is_on_edupython = True
except: is_on_edupython = False

if is_on_edupython:
    os.system("start powershell.exe")