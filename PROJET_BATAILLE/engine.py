"""
Module : engine.py
Gère les règles de placement flexible et la détection des tirs.
"""
from __future__ import annotations

import random
from typing import Literal

Position = tuple[int, int]
ResultatTir = Literal["DÉJÀ TIRÉ", "COULÉ", "TOUCHÉ", "DANS L'EAU"]
Orientation = Literal["H", "V"]


class BatailleEngine:
    def __init__(self) -> None:
        self.ma_grille: dict[Position, str] = {}
        self.bateaux_places: list[list[Position]] = []
        self.tailles_a_placer: list[int] = [1, 2, 3, 4, 5]
        self.index_taille: int = 0
        self.bateau_en_cours: list[Position] = []
        self.tirs_recus: set[Position] = set()

    def valider_clic(self, l: int, c: int) -> tuple[bool, str]:
        """Vérifie si la case (l,c) peut compléter le bateau en cours."""
        if (l, c) in self.ma_grille:
            return False, "Case déjà occupée !"

        if len(self.bateau_en_cours) == 0:
            return True, "Premier point"

        # Vérifier si la case touche au moins UNE des cases déjà placées.
        touche_un_morceau: bool = False
        for bl, bc in self.bateau_en_cours:
            if (abs(l - bl) == 1 and c == bc) or (abs(c - bc) == 1 and l == bl):
                touche_un_morceau = True
                break

        if not touche_un_morceau:
            return False, "La case doit toucher un morceau du bateau déjà placé !"

        # Vérifier l'alignement global : toutes les cases sur la même ligne ou colonne.
        lignes: set[int] = {pos[0] for pos in self.bateau_en_cours}
        lignes.add(l)
        colonnes: set[int] = {pos[1] for pos in self.bateau_en_cours}
        colonnes.add(c)

        if len(lignes) > 1 and len(colonnes) > 1:
            return False, "Le bateau doit être en ligne droite (Horizontal ou Vertical) !"

        return True, "Ok"

    def ajouter_point(self, l: int, c: int) -> bool:
        self.bateau_en_cours.append((l, c))
        self.ma_grille[(l, c)] = "B"

        if len(self.bateau_en_cours) == self.tailles_a_placer[self.index_taille]:
            self.bateaux_places.append(list(self.bateau_en_cours))
            self.bateau_en_cours = []
            self.index_taille += 1
            return True

        return False

    def placer_bateaux_aleatoire(self) -> None:
        for taille in self.tailles_a_placer:
            place: bool = False
            while not place:
                orient: Orientation = random.choice(["H", "V"])
                l: int = random.randint(1, 10)
                c: int = random.randint(1, 10)
                pos: list[Position] = [
                    (l, c + i) if orient == "H" else (l + i, c)
                    for i in range(taille)
                ]

                if all(1 <= p[0] <= 10 and 1 <= p[1] <= 10 and p not in self.ma_grille for p in pos):
                    for p in pos:
                        self.ma_grille[p] = "B"
                    self.bateaux_places.append(pos)
                    place = True

    def verifier_tir(self, l: int, c: int) -> ResultatTir:
        if (l, c) in self.tirs_recus:
            return "DÉJÀ TIRÉ"

        self.tirs_recus.add((l, c))

        if (l, c) in self.ma_grille:
            self.ma_grille[(l, c)] = "X"
            for bateau in self.bateaux_places:
                if (l, c) in bateau:
                    if all(self.ma_grille[p] == "X" for p in bateau):
                        return "COULÉ"
                    return "TOUCHÉ"

        return "DANS L'EAU"

