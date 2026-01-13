# Script de détection des interprétateurs Python
# Détecte toutes les installations Python et permet de choisir pour lancer tron_prof.py

Write-Host "=== Détection des interprétateurs Python ===" -ForegroundColor Cyan
Write-Host ""

# Fonction pour obtenir les informations détaillées d'un exécutable Python
function Get-PythonInfo {
    param($Path)
    
    try {
        $version = & $Path --version 2>&1
        $arch = & $Path -c "import platform; print(platform.architecture()[0])" 2>$null
        $location = & $Path -c "import sys; print(sys.executable)" 2>$null
        
        [PSCustomObject]@{
            Chemin = $Path
            Version = $version
            Architecture = $arch
            Emplacement = $location
        }
    } catch {
        return $null
    }
}

# Tableau pour stocker tous les interprétateurs trouvés
$pythonInstances = @()

# 1. Recherche via la commande 'where' (CMD)
Write-Host "[1] Recherche via la commande système..." -ForegroundColor Yellow
$wherePython = where.exe python 2>$null
if ($wherePython) {
    foreach ($path in $wherePython) {
        $info = Get-PythonInfo -Path $path
        if ($info) { $pythonInstances += $info }
    }
}

# 2. Recherche dans PATH
Write-Host "[2] Recherche dans les variables PATH..." -ForegroundColor Yellow
$pathDirs = $env:PATH -split ';'
foreach ($dir in $pathDirs) {
    if (Test-Path $dir) {
        $pythonExes = Get-ChildItem -Path $dir -Filter "python*.exe" -ErrorAction SilentlyContinue
        foreach ($exe in $pythonExes) {
            $info = Get-PythonInfo -Path $exe.FullName
            if ($info) { $pythonInstances += $info }
        }
    }
}

# 3. Recherche dans les emplacements standards
Write-Host "[3] Recherche dans les emplacements standards..." -ForegroundColor Yellow
$standardPaths = @(
    "$env:LOCALAPPDATA\Programs\Python",
    "$env:USERPROFILE\AppData\Local\Programs\Python",
    "C:\Python*",
    "C:\\EduPython\App",
    "$env:PROGRAMFILES\Python*",
    "${env:PROGRAMFILES(x86)}\Python*"
)

foreach ($path in $standardPaths) {
    $folders = Get-Item $path -ErrorAction SilentlyContinue
    foreach ($folder in $folders) {
        $pythonExes = Get-ChildItem -Path $folder -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue
        foreach ($exe in $pythonExes) {
            $info = Get-PythonInfo -Path $exe.FullName
            if ($info) { $pythonInstances += $info }
        }
    }
}

# 4. Recherche via le Python Launcher (py.exe)
Write-Host "[4] Recherche via le Python Launcher..." -ForegroundColor Yellow
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pyList = py -0p 2>$null
    if ($pyList) {
        foreach ($line in $pyList -split "`n") {
            if ($line -match '\s+(.+\.exe)') {
                $path = $matches[1].Trim()
                $info = Get-PythonInfo -Path $path
                if ($info) { $pythonInstances += $info }
            }
        }
    }
}

# Suppression des doublons
$pythonInstances = $pythonInstances | Sort-Object Emplacement -Unique

# Affichage des résultats
Write-Host ""
Write-Host "=== Résultats ===" -ForegroundColor Cyan
Write-Host ""

if ($pythonInstances.Count -eq 0) {
    Write-Host "Aucun interprétateur Python détecté sur ce système." -ForegroundColor Red
    Write-Host "Veuillez installer Python depuis https://www.python.org" -ForegroundColor Yellow
    exit
}

Write-Host "Nombre d'interprétateurs trouvés: $($pythonInstances.Count)" -ForegroundColor Green
Write-Host ""

$i = 1
foreach ($python in $pythonInstances) {
    Write-Host "[$i] Python détecté" -ForegroundColor Green
    Write-Host "    Version      : $($python.Version)" -ForegroundColor White
    Write-Host "    Architecture : $($python.Architecture)" -ForegroundColor White
    Write-Host "    Emplacement  : $($python.Emplacement)" -ForegroundColor White
    Write-Host ""
    $i++
}

# Demander à l'utilisateur de choisir un interpréteur
Write-Host "=== Lancement de tron_prof.py ===" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Quel interpréteur voulez-vous utiliser pour démarrer tron_prof.py ? (1-$($pythonInstances.Count))"

# Validation du choix
if ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le $pythonInstances.Count) {
    $selectedPython = $pythonInstances[[int]$choice - 1]
    Write-Host ""
    Write-Host "Interpréteur sélectionné:" -ForegroundColor Green
    Write-Host "  $($selectedPython.Version) - $($selectedPython.Emplacement)" -ForegroundColor White
    Write-Host ""
    
    # Liste des scripts à essayer dans l'ordre
    $scriptNames = @("tron_prof.py", "tron_prof_1.py", "tron_prof_2.py", "tron_prof_3.py")
    $scriptFound = $false
    
    foreach ($scriptName in $scriptNames) {
        $scriptPath = Join-Path $PSScriptRoot $scriptName
        
        if (Test-Path $scriptPath) {
            Write-Host "=== Préparation de $scriptName ===" -ForegroundColor Cyan
            Write-Host ""
            
            # Si c'est tron_prof_1.py, vérifier et installer pynput
            if ($scriptName -eq "tron_prof_1.py") {
                Write-Host "$scriptName nécessite la bibliothèque 'pynput'" -ForegroundColor Yellow
                $installPynput = Read-Host "Voulez-vous installer/vérifier pynput ? (O/N)"
                
                if ($installPynput -eq 'O' -or $installPynput -eq 'o') {
                    Write-Host ""
                    Write-Host "Recherche de pip..." -ForegroundColor Yellow
                    
                    # Trouver pip associé à l'interpréteur Python sélectionné
                    $pythonDir = Split-Path $selectedPython.Emplacement
                    $pipPath = Join-Path $pythonDir "Scripts\pip.exe"
                    
                    if (-not (Test-Path $pipPath)) {
                        $pipPath = Join-Path $pythonDir "pip.exe"
                    }
                    
                    # Essayer avec python -m pip si pip.exe n'est pas trouvé
                    if (-not (Test-Path $pipPath)) {
                        Write-Host "Test de pip avec 'python -m pip'..." -ForegroundColor Yellow
                        $pipTest = & $selectedPython.Emplacement -m pip --version 2>&1
                        
                        if ($LASTEXITCODE -eq 0) {
                            Write-Host "pip trouvé et fonctionnel: $pipTest" -ForegroundColor Green
                            $usePipModule = $true
                        } else {
                            Write-Host "ERREUR: pip n'a pas été trouvé pour cet interpréteur Python." -ForegroundColor Red
                            Write-Host "Passage au script suivant..." -ForegroundColor Yellow
                            Write-Host ""
                            continue
                        }
                    } else {
                        Write-Host "pip trouvé: $pipPath" -ForegroundColor Green
                        $pipVersion = & $pipPath --version 2>&1
                        Write-Host "Version: $pipVersion" -ForegroundColor White
                        $usePipModule = $false
                    }
                    
                    Write-Host ""
                    Write-Host "Vérification de pynput..." -ForegroundColor Yellow
                    
                    # Vérifier si pynput est déjà installé
                    $pynputCheck = & $selectedPython.Emplacement -c "import pynput; print('OK')" 2>$null
                    
                    if ($pynputCheck -eq "OK") {
                        Write-Host "pynput est déjà installé et fonctionnel !" -ForegroundColor Green
                    } else {
                        Write-Host "Installation de pynput..." -ForegroundColor Yellow
                        
                        if ($usePipModule) {
                            & $selectedPython.Emplacement -m pip install pynput
                        } else {
                            & $pipPath install pynput
                        }
                        
                        if ($LASTEXITCODE -eq 0) {
                            Write-Host ""
                            Write-Host "Vérification de l'installation..." -ForegroundColor Yellow
                            $pynputVerify = & $selectedPython.Emplacement -c "import pynput; print('OK')" 2>$null
                            
                            if ($pynputVerify -eq "OK") {
                                Write-Host "pynput installé et fonctionnel !" -ForegroundColor Green
                            } else {
                                Write-Host "ERREUR: pynput installé mais ne fonctionne pas correctement." -ForegroundColor Red
                                Write-Host "Passage au script suivant..." -ForegroundColor Yellow
                                Write-Host ""
                                continue
                            }
                        } else {
                            Write-Host "ERREUR: L'installation de pynput a échoué." -ForegroundColor Red
                            Write-Host "Passage au script suivant..." -ForegroundColor Yellow
                            Write-Host ""
                            continue
                        }
                    }
                    Write-Host ""
                } else {
                    Write-Host "Installation de pynput refusée. Passage au script suivant..." -ForegroundColor Yellow
                    Write-Host ""
                    continue
                }
            }
            
            Write-Host "Lancement de $scriptName dans une nouvelle fenêtre..." -ForegroundColor Yellow
            Write-Host ""
            
            # Créer une commande pour lancer le script dans une nouvelle fenêtre PowerShell
            $command = "& '$($selectedPython.Emplacement)' '$scriptPath'; Write-Host ''; Write-Host 'Appuyez sur une touche pour fermer cette fenêtre...' -ForegroundColor Yellow; `$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')"
            
            # Lancer dans une nouvelle fenêtre PowerShell
            Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
            
            Write-Host "Une nouvelle fenêtre s'est ouverte avec $scriptName" -ForegroundColor Green
            Write-Host ""
            
            # Demander si ça fonctionne
            $response = Read-Host "Est-ce que $scriptName fonctionne correctement ? (O/N)"
            
            if ($response -eq 'O' -or $response -eq 'o') {
                Write-Host ""
                Write-Host "Parfait ! Le script $scriptName fonctionne." -ForegroundColor Green
                $scriptFound = $true
                break
            } else {
                Write-Host ""
                Write-Host "$scriptName ne fonctionne pas. Essai du script suivant..." -ForegroundColor Yellow
                Write-Host ""
            }
        } else {
            Write-Host "Le fichier $scriptName n'existe pas. Passage au suivant..." -ForegroundColor Yellow
            Write-Host ""
        }
    }
    
    if (-not $scriptFound) {
        Write-Host ""
        Write-Host "ERREUR: Aucun script fonctionnel n'a été trouvé." -ForegroundColor Red
        Write-Host "Scripts recherchés: $($scriptNames -join ', ')" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Veuillez vérifier que les fichiers Python se trouvent dans le même dossier que ce script." -ForegroundColor Yellow
    }
} else {
    Write-Host "Choix invalide. Veuillez relancer le script et choisir un numéro entre 1 et $($pythonInstances.Count)." -ForegroundColor Red
}

Write-Host ""
Write-Host "Appuyez sur une touche pour quitter..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")