"""
Module : engine.py
Gère les règles de placement flexible et la détection des tirs.
"""
import random

class BatailleEngine:
    def __init__(self):
        self.ma_grille = {} 
        self.bateaux_places = []
        self.tailles_a_placer = [1, 2, 3, 4, 5]
        self.index_taille = 0
        self.bateau_en_cours = []
        self.tirs_recus = set()

    def valider_clic(self, l, c):
        """Vérifie si la case (l,c) peut compléter le bateau en cours."""
        if (l, c) in self.ma_grille:
            return False, "Case déjà occupée !"
        
        if len(self.bateau_en_cours) == 0:
            return True, "Premier point"

        # Vérifier si la case touche au moins UNE des cases déjà placées
        touche_un_morceau = False
        for (bl, bc) in self.bateau_en_cours:
            if (abs(l - bl) == 1 and c == bc) or (abs(c - bc) == 1 and l == bl):
                touche_un_morceau = True
                break
        
        if not touche_un_morceau:
            return False, "La case doit toucher un morceau du bateau déjà placé !"

        # Vérifier l'alignement global (toutes les cases sur la même ligne ou colonne)
        lignes = {pos[0] for pos in self.bateau_en_cours}
        lignes.add(l)
        colonnes = {pos[1] for pos in self.bateau_en_cours}
        colonnes.add(c)

        if len(lignes) > 1 and len(colonnes) > 1:
            return False, "Le bateau doit être en ligne droite (Horizontal ou Vertical) !"

        return True, "Ok"

    def ajouter_point(self, l, c):
        self.bateau_en_cours.append((l, c))
        self.ma_grille[(l, c)] = "B"
        if len(self.bateau_en_cours) == self.tailles_a_placer[self.index_taille]:
            self.bateaux_places.append(list(self.bateau_en_cours))
            self.bateau_en_cours = []
            self.index_taille += 1
            return True 
        return False

    def placer_bateaux_aleatoire(self):
        for taille in self.tailles_a_placer:
            place = False
            while not place:
                orient = random.choice(["H", "V"])
                l, c = random.randint(1, 10), random.randint(1, 10)
                pos = [(l, c+i) if orient=="H" else (l+i, c) for i in range(taille)]
                if all(1<=p[0]<=10 and 1<=p[1]<=10 and p not in self.ma_grille for p in pos):
                    for p in pos: self.ma_grille[p] = "B"
                    self.bateaux_places.append(pos)
                    place = True

    def verifier_tir(self, l, c):
        if (l, c) in self.tirs_recus: return "DÉJÀ TIRÉ"
        self.tirs_recus.add((l, c))
        if (l, c) in self.ma_grille:
            self.ma_grille[(l, c)] = "X"
            for b in self.bateaux_places:
                if (l, c) in b:
                    if all(self.ma_grille[p] == "X" for p in b): return "COULÉ"
                    return "TOUCHÉ"
        return "DANS L'EAU"