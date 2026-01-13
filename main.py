import subprocess
import os

def executer_script_powershell(chemin_script):
    
    if not os.path.exists(chemin_script):
        print(f"Erreur: Le fichier {chemin_script} n'existe pas")
        return
    
    print(f"Exécution de: {chemin_script}\n")
    subprocess.call([
        "powershell.exe",
        "-ExecutionPolicy", "Bypass",
        "-File", chemin_script
    ])
    
    print("\nScript terminé")


# Utilisation
if __name__ == "__main__":
    executer_script_powershell("test.ps1")