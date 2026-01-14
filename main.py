import os

def powershell_exec(chemin_script):
    if not os.path.exists(chemin_script):
        print(f"Erreur: Le fichier {chemin_script} n'existe pas")
        return False

    print(f"Ouverture de PowerShell pour: {chemin_script}")

    os.system(f'start powershell -NoExit -ExecutionPolicy Bypass -File "{chemin_script}"')

    return True

powershell_exec("test.ps1")
print("Si ça fonctionne pas, veuillez demarer le ps1 manuellement et si le ps1 fonctionne pas veuillez démarer les fichiers 1 par 1.")