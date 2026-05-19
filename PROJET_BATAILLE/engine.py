"""
PROJET : BATAILLE NAVALE
Module : engine.py
Description : Gère les règles de placement et la détection des tirs.
Fait par Christina et Bianca le 12.05.2026
"""

from __future__ import annotations
import random

POSITION = tuple[int, int]
RESULTAT_TIR = ["DÉJÀ TIRÉ", "COULÉ", "TOUCHÉ", "DANS L'EAU"]
ORIENTATION = ["H", "V"]


class BatailleEngine:
    """
    Moteur logique gérant l'état d'une grille de jeu.
    
    Attributs:
        ma_grille (dict): Positions occupées par les bateaux.
        bateaux_places (list): Liste des coordonnées de chaque bateau.
        tailles_a_placer (list): Liste des tailles des bateaux restant à poser.
    """
    
    def __init__(self) -> None:
        """Initialise une nouvelle instance du moteur de jeu."""
        self.ma_grille = {}
        self.bateaux_places = []
        self.tailles_a_placer = [1, 2, 3, 4, 5]
        self.index_taille = 0
        self.bateau_en_cours = []
        self.tirs_recus = set()

    def valider_clic(self, ligne: int, colonne: int) -> tuple[bool, str]:
        """
        Vérifie si la case (ligne, colonne) est valide pour le bateau actuel.

        Args:
            ligne (int): Coordonnée verticale.
            colone (int): Coordonnée horizontale.

        Returns:
            tuple[bool, str]: (Est valide, Message d'explication).
        """

        if (ligne, colonne) in self.ma_grille:
            return False, "Case déjà occupée !"

        if len(self.bateau_en_cours) == 0:
            return True, "Premier point"

        # Vérifier si la case touche au moins UNE des cases déjà placées.
        #abs indique une valeure absolue
        touche_un_morceau = False
        for bl, bc in self.bateau_en_cours:
            if (abs(ligne - bl) == 1 and colonne == bc) or (abs(colonne - bc) == 1 and ligne == bl):
                touche_un_morceau = True
                break

        if touche_un_morceau == False :
            return False, "La case doit toucher un morceau du bateau déjà placé !"

       # Vérifier l'alignement global : toutes les cases sur la même ligne ou colonne.
        lignes = set()
        colonnes = set()
        
        for pos in self.bateau_en_cours:
            lignes.add(pos[0])
            colonnes.add(pos[1])
        
        lignes.add(ligne)
        colonnes.add(colonne)

        if len(lignes) > 1 and len(colonnes) > 1:
            return False, "Le bateau doit être en ligne droite (Horizontal ou Vertical) !"
            
        return True, "Ok"

    def ajouter_point(self, ligne: int, colonne: int) -> bool:
        """
        Ajoute une case au bateau en cours.

        Returns:
            bool: True si le bateau est terminé, False sinon.
        """
        
        self.bateau_en_cours.append((ligne, colonne))
        self.ma_grille[(ligne, colonne)] = "B"

        if len(self.bateau_en_cours) == self.tailles_a_placer[self.index_taille]:
            self.bateaux_places.append(list(self.bateau_en_cours))
            self.bateau_en_cours = []
            self.index_taille += 1
            return True

        return False

    def placer_bateaux_aleatoire(self) -> None:
        """Place automatiquement tous les bateaux
            (pour la version contre ordinateur)."""
        for taille in self.tailles_a_placer:
            place = False
            while place == False:
                orient = random.choice(["H", "V"])
                ligne = random.randint(1, 10)
                colonne = random.randint(1, 10)
                pos = []
                for i in range(taille):
                    if orient == "H":
                        pos.append((ligne,colonne + i))
                    else:
                        pos.append((ligne + i,colonne))
                    
                valide = True

                #s'assure qu'un point ne va en dessous de 1 ni ne dépasse 10
                #et qu'il ne soit pas déjà placé    
                for p in pos:
                    if p[0]< 1 or p[0]>10 or p[1]<1 or p[1]>10 or p in self.ma_grille:
                        valide = False
                #tant qu'une case qui porte un bateau n'est pas encore touchée,
                #elle porte la marque "B"
                if valide:
                    for p in pos:
                        self.ma_grille[p]="B"
                    self.bateaux_places.append(pos)
                    place = True

    def verifier_tir(self, ligne: int, colonne: int) -> RESULTAT_TIR:
        """
        Vérifie l'éffet d'un tir
        ( aucun (déjà tiré),touché, coulé ou dans l'eau)

        Returns:
            RESULTAT_TIR: Résultat de l'attaque.
        """
        
        if (ligne, colonne) in self.tirs_recus:
            return "DÉJÀ TIRÉ"

        self.tirs_recus.add((ligne, colonne))
        
        #lorsqu'une case est touchée elle prend la marque X
        if (ligne, colonne) in self.ma_grille:
            self.ma_grille[(ligne, colonne)] = "X"
            
            for bateau in self.bateaux_places:
                if (ligne, colonne) in bateau:
                    coule = True
                    for p in bateau:
                        if self.ma_grille[p] != "X":
                            coule = False
                    if coule:
                        return "COULÉ"
                    return "TOUCHÉ"
                    
        return "DANS L'EAU"
    
    def tous_coules(self) -> bool:
        """Vérifie si la partie est terminée (tous les bateaux détruits)."""
        for bateau in self.bateaux_places:
            for p in bateau:
                if self.ma_grille[p] != "X":
                    return False
        return True

