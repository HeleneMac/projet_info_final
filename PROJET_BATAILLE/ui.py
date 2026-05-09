from __future__ import annotations

import tkinter as tk
from typing import Callable, Literal

Grille = Literal["moi", "adversaire"]
Position = tuple[int, int]
CallbackCase = Callable[[int, int], None]


class BatailleUI:
    """Interface graphique du jeu Bataille Navale.
    Affiche les grilles du joueur et de l'adversaire.
    """

    def __init__(self, root: tk.Tk, callback_tir: CallbackCase, callback_placement: CallbackCase) -> None:
        self.root: tk.Tk = root
        self.boutons_ma_flotte: dict[Position, tk.Button] = {}
        self.bateau_adversaire: dict[Position, tk.Button] = {}

        frame_flotte: tk.Frame = tk.Frame(root)
        frame_flotte.pack(side=tk.LEFT, padx=20, pady=20)

        frame_adversaire: tk.Frame = tk.Frame(root)
        frame_adversaire.pack(side=tk.RIGHT, padx=20, pady=20)

        tk.Label(frame_flotte, text="MA FLOTTE", font=("Arial", 10, "bold")).grid(row=0, column=1, columnspan=10)
        tk.Label(frame_adversaire, text="ATTAQUE", font=("Arial", 10, "bold")).grid(row=0, column=1, columnspan=10)

        for ligne in range(1, 11):
            for colonne in range(1, 11):
                bouton_flotte: tk.Button = tk.Button(
                    frame_flotte,
                    width=3,
                    bg="#E1F5FE",
                    command=lambda ligne=ligne, colonne=colonne: callback_placement(ligne, colonne),
                )
                bouton_flotte.grid(row=ligne, column=colonne)
                self.boutons_ma_flotte[(ligne, colonne)] = bouton_flotte

                bouton_adversaire: tk.Button = tk.Button(
                    frame_adversaire,
                    width=3,
                    bg="#ECEFF1",
                    command=lambda ligne=ligne, colonne=colonne: callback_tir(ligne, colonne),
                )
                bouton_adversaire.grid(row=ligne, column=colonne)
                self.bateau_adversaire[(ligne, colonne)] = bouton_adversaire

    def colorier(self, grille: Grille, ligne: int, colonne: int, couleur: str) -> None:
        target: dict[Position, tk.Button]
        if grille == "moi":
            target = self.boutons_ma_flotte
        else:
            target = self.bateau_adversaire

        if (ligne, colonne) in target:
            target[(ligne, colonne)].config(bg=couleur)

    def set_titre(self, texte: str) -> None:
        self.root.title(f"Bataille Navale - {texte}")

