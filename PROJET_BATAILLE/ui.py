"""
PROJET : BATAILLE NAVALE
Module : ui.py
Description : Interface graphique (GUI) gérant l'affichage des grilles et des boutons.
Fait par Bianca et Christina le 12.05.2026
"""

from __future__ import annotations
import tkinter as tk
from typing import Callable, Literal

GRILLE = Literal["moi", "adversaire"]
POSITION = tuple[int, int]
CALLBACKCASE = Callable[[int, int], None]


class BatailleUI:
    """
    Gère l'interface utilisateur de la Bataille Navale.
    
    Cette classe crée la fenêtre de jeu, dessine les deux grilles (joueur et adversaire)
    avec des étiquettes de coordonnées (A-J, 1-10) et gère les mises à jour visuelles.
    
    Attributes:
        root (tk.Tk): La fenêtre principale de l'application.
        boutons_ma_flotte (dict): Dictionnaire stockant les boutons de la grille joueur.
        bateau_adversaire (dict): Dictionnaire stockant les boutons de la grille adverse.
    """

    def __init__(self, root: tk.Tk, callback_tir: CALLBACKCASE, callback_placement: CALLBACKCASE) -> None:
        """
        Initialise l'interface, configure les couleurs de fond et crée les grilles.

        Args:
            root (tk.Tk): Fenêtre parente.
            callback_tir (CALLBACKCASE): Fonction à appeler lors d'un tir.
            callback_placement (CALLBACKCASE): Fonction à appeler lors du placement.
        """
        self.root = root
        self.boutons_ma_flotte = {}
        self.bateau_adversaire = {}

        self.root.configure(bg="#263238")
        self.main_frame = tk.Frame(root, bg="#263238")
        self.main_frame.pack(fill="both", expand=True)
        
        self.lettres = "ABCDEFGHIJ"

        self.creer_grille_complete("MA FLOTTE", tk.LEFT, self.boutons_ma_flotte, callback_placement, "#E1F5FE")
        self.creer_grille_complete("ATTAQUE ADVERSAIRE", tk.RIGHT, self.bateau_adversaire, callback_tir, "#ECEFF1")
        
    def creer_grille_complete(self, titre: str, cote: int, dico: dict, callback: CALLBACKCASE, bg_color: str):
        """
        Construit une grille 10x10 avec des labels pour les colonnes (A-J) et les lignes (1-10).

        Args:
            titre (str): Nom affiché au-dessus de la grille.
            cote (int): Positionnement (tk.LEFT ou tk.RIGHT).
            dico (dict): Dictionnaire pour stocker les références des boutons créés.
            callback (CALLBACK_CLIC): Action déclenchée par le clic sur un bouton.
            bg_color (str): Couleur de fond par défaut des cases.
        """
        
        frame_ext = tk.Frame(self.main_frame, padx=20, pady=20, bg="#263238")
        frame_ext.pack(side=cote)

        tk.Label(frame_ext, text=titre, font=("Impact", 16), fg="white", bg="#263238").pack(pady=5)
            
          
        grid_frame = tk.Frame(frame_ext, bg="#37474F", padx=5, pady=5)
        grid_frame.pack()

      
        for c in range(10):
            tk.Label(grid_frame, text=self.lettres[c], width=4, bg="#37474F", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=c+1)

        for l in range(1, 11):
            tk.Label(grid_frame, text=str(l), height=2, bg="#37474F", fg="white", font=("Arial", 10, "bold")).grid(row=l, column=0, padx=5)
                
            for c in range(1, 11):
                btn = tk.Button(
                    grid_frame,
                    width=4,
                    height=2,
                    bg=bg_color,
                    relief="flat",
                    borderwidth=1,
                    command=lambda r=l, col=c: callback(r, col)
                )
                btn.grid(row=l, column=c, padx=1, pady=1)
                dico[(l, c)] = btn

    def colorier(self, grille: GRILLE, ligne: int, colonne: int, couleur: str) -> None:
        """
        Met à jour l'apparence d'une case (couleur et symbole) selon le résultat du jeu.

        Args:
            grille (GRILLE_TYPE): "moi" pour la flotte du joueur, "adversaire" pour l'attaque.
            ligne (int): Index de la ligne (1-10).
            colonne (int): Index de la colonne (1-10).
            couleur (str): Identifiant de l'état (red=touché, black=raté, blue=placé).
        """
        target = self.boutons_ma_flotte if grille == "moi" else self.bateau_adversaire
        
        if (ligne, colonne) in target:
            if couleur == "red":
                # Tir réussi : Rouge avec un X
                target[(ligne, colonne)].config(bg="#FF5252", text="X", fg="white")
            elif couleur == "black":
                # Tir raté : Gris-bleu avec un ~ (vague)
                target[(ligne, colonne)].config(bg="#546E7A", text="~", fg="white")
            elif couleur == "blue":
                # Bateau placé : Bleu
                target[(ligne, colonne)].config(bg="#0288D1")
            else:
                # Couleur générique
                target[(ligne, colonne)].config(bg=couleur)

    def set_titre(self, texte: str) -> None:
        """Modifie le titre de la fenêtre principale."""
        self.root.title(f"BATAILLE NAVALE - {texte}")
