# Tableau de 100 cases (grille 10x10 aplatie)
# 0 = case vide, 1 = trace de l'animal
grille = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 1, 0, 0, 0, 0,
    0, 0, 0, 1, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 1, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 1, 1, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

def calculer_centre_gravite(grille):
    """Calcule le centre de gravité et retourne l'index dans le tableau"""
    somme_indices = 0
    nombre_traces = 0
    
    for i in range(len(grille)):
        if grille[i] == 1:
            somme_indices += i
            nombre_traces += 1
    
    if nombre_traces == 0:
        return None
    
    centre_index = somme_indices / nombre_traces
    centre_arrondi = round(centre_index)
    
    return centre_arrondi

# Calculer et afficher le centre de gravité
centre = calculer_centre_gravite(grille)
print(f"Centre de gravité à l'index : {centre}")
print(f"Valeur à cette position : {grille[centre]}")