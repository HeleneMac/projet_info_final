"""
Module : main.py
Contrôleur principal avec guidage réseau pas à pas.
"""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox
from typing import Literal

from engine import BatailleEngine, ResultatTir
from network import Connexion
from ui import BatailleUI, Grille

PORT: int = 9999
ModeJeu = Literal["SOLO", "MULTI"]
Position = tuple[int, int]


class Controle:
    def __init__(self) -> None:
        self.racine: tk.Tk = tk.Tk()
        self.engine: BatailleEngine = BatailleEngine()
        self.engine_ia: BatailleEngine | None = None
        self.net: Connexion = Connexion()
        self.ui: BatailleUI = BatailleUI(self.racine, self.on_tir, self.on_place)

        self.pret_moi: bool = False
        self.pret_adv: bool = False
        self.mon_tour: bool = False
        self.mode: ModeJeu | None = None
        self.tirs_ordi: set[Position] = set()
        self.tirs_joueur: set[Position] = set()

        self.texte: tk.Label = tk.Label(self.racine, text="Adresse de l'hôte:", font=30)
        self.host_adresse: tk.Entry = tk.Entry(self.racine)
        self.bouton_connexion: tk.Button = tk.Button(
            self.racine,
            text="Connexion",
            command=self.connecter_client,
        )

        self.config_initiale()

    def config_initiale(self) -> None:
        """Permet de choisir le mode et de connecter au besoin selon si l'ordi est hôte ou client."""
        print("\n" + "=" * 40)
        print(" BIENVENUE DANS LA BATAILLE NAVALE")
        print("=" * 40)

        choix: bool = messagebox.askyesno("Seul/Multijoueur", "Jouez-vous seul ?")

        if choix:
            self.mode = "SOLO"
            self.pret_adv = True
            self.engine_ia = BatailleEngine()
            self.engine_ia.placer_bateaux_aleatoire()
            self.mon_tour = True
            messagebox.showinfo("Placer bateaux", "Mode Solo : Placez vos bateaux !")
        else:
            self.mode = "MULTI"
            role: bool = messagebox.askyesno("Client/Serveur", "Êtes-vous l'hôte ?")
            if role:
                self.net.serveur(PORT)
                self.net.ecouter(self.handle_data)
                self.mon_tour = True
            else:
                messagebox.showinfo("Connexion", "Entrez l'adresse de l'hôte en haut à gauche")
                self.texte.place(x=5, y=5)
                self.host_adresse.place(x=135, y=5)
                self.bouton_connexion.place(x=260, y=3)

    def connecter_client(self) -> None:
        """Connecte le client puis démarre l'écoute réseau."""
        self.net.client(self.host_adresse.get(), PORT)
        self.net.ecouter(self.handle_data)
        messagebox.showinfo("Placer bateaux", "Connecté ! Placez vos bateaux !")

    def on_place(self, ligne: int, colonne: int) -> None:
        """Place les bateaux tant que le joueur n'est pas prêt."""
        if self.pret_moi:
            return

        valide: bool
        msg: str
        valide, msg = self.engine.valider_clic(ligne, colonne)

        if not valide:
            messagebox.showwarning("Attention", msg)
            return

        fini: bool = self.engine.ajouter_point(ligne, colonne)
        self.ui.colorier("moi", ligne, colonne, "blue")

        if fini:
            if self.engine.index_taille < len(self.engine.tailles_a_placer):
                taille: int = self.engine.tailles_a_placer[self.engine.index_taille]
                messagebox.showinfo("Suivant", f"Bateau terminé. Placez le suivant (taille {taille})")
            else:
                self.pret_moi = True
                if self.mode == "MULTI":
                    self.net.envoyer("READY")
                self.verifier_demarrage()

    def verifier_demarrage(self) -> None:
        """Vérifie si les deux joueurs sont prêts et met à jour le titre."""
        if self.pret_moi and self.pret_adv:
            if self.mon_tour:
                self.ui.set_titre("À VOUS DE JOUER")
            else:
                self.ui.set_titre("ATTENTE ADVERSAIRE")
            messagebox.showinfo("Début", "Tout le monde est prêt ! Attaquez !")
        elif self.pret_moi:
            self.ui.set_titre("ATTENTE ADVERSAIRE")
            messagebox.showinfo("Attente", "Vous avez fini ! On attend l'adversaire.")
        else:
            self.ui.set_titre("PLACEZ VOS BATEAUX")

    def on_tir(self, ligne: int, colonne: int) -> None:
        """Gère un tir du joueur."""
        if not self.pret_moi or not self.pret_adv:
            self.afficher_notification("Attente", "Le placement n'est pas fini !")
            return

        if not self.mon_tour:
            self.afficher_notification("Tour", "C'est le tour de l'adversaire !")
            return

        if (ligne, colonne) in self.tirs_joueur:
            self.afficher_notification("Déjà tiré", "Déjà tiré sur cette case, choisissez une autre case.")
            self.ui.set_titre("À VOUS DE JOUER !")
            return

        self.tirs_joueur.add((ligne, colonne))

        if self.mode == "SOLO":
            if self.engine_ia is None:
                return

            resultat: ResultatTir = self.engine_ia.verifier_tir(ligne, colonne)
            self.traiter_resultat_tir("adversaire", ligne, colonne, resultat)

            if resultat == "DÉJÀ TIRÉ":
                self.mon_tour = True
                self.ui.set_titre("À VOUS DE JOUER !")
                return

            self.mon_tour = False
            self.racine.after(800, self.faire_jouer_ordi)
        else:
            self.net.envoyer(f"TIR:{ligne},{colonne}")
            self.mon_tour = False
            self.ui.set_titre("ATTENTE ADVERSAIRE...")

    def handle_data(self, data: str) -> None:
        if data == "READY":
            self.pret_adv = True
            self.racine.after(0, self.verifier_demarrage)
        elif data.startswith("TIR:"):
            ligne: int
            colonne: int
            ligne, colonne = map(int, data.split(":")[1].split(","))
            resultat: ResultatTir = self.engine.verifier_tir(ligne, colonne)

            if resultat in ["TOUCHÉ", "COULÉ"]:
                self.ui.colorier("moi", ligne, colonne, "red")
            else:
                self.ui.colorier("moi", ligne, colonne, "black")

            self.net.envoyer(f"RES:{ligne},{colonne},{resultat}")
            self.mon_tour = True
            self.ui.set_titre("À VOUS DE JOUER !")
            self.afficher_notification("Alerte", f"L'adversaire a tiré en {ligne},{colonne} : {resultat} !")
        elif data.startswith("RES:"):
            ligne_str: str
            colonne_str: str
            resultat_str: str
            ligne_str, colonne_str, resultat_str = data.split(":")[1].split(",")
            self.traiter_resultat_tir("adversaire", int(ligne_str), int(colonne_str), resultat_str)

    def traiter_resultat_tir(self, grille: Grille, ligne: int, colonne: int, resultat: str) -> None:
        if resultat == "DÉJÀ TIRÉ":
            self.afficher_notification("Déjà tiré", "Déjà tiré sur cette case, choisissez une autre case.")
            self.mon_tour = True
            self.ui.set_titre("À VOUS DE JOUER !")
            return

        self.ui.colorier(grille, ligne, colonne, "red" if resultat in ["TOUCHÉ", "COULÉ"] else "black")
        self.afficher_notification("Résultat", f"Tir en {ligne},{colonne} : {resultat}")

        if self.mode == "MULTI" and not self.mon_tour:
            self.ui.set_titre("TOUR ADVERSAIRE")

    def faire_jouer_ordi(self) -> None:
        ligne: int = random.randint(1, 10)
        colonne: int = random.randint(1, 10)

        while (ligne, colonne) in self.tirs_ordi:
            ligne = random.randint(1, 10)
            colonne = random.randint(1, 10)

        self.tirs_ordi.add((ligne, colonne))
        resultat: ResultatTir = self.engine.verifier_tir(ligne, colonne)

        if resultat in ["TOUCHÉ", "COULÉ"]:
            self.ui.colorier("moi", ligne, colonne, "red")
        else:
            self.ui.colorier("moi", ligne, colonne, "black")

        self.afficher_notification("Tour ordinateur", f"L'ordinateur a tiré en {ligne},{colonne} : {resultat}")
        self.mon_tour = True
        self.ui.set_titre("À VOUS DE JOUER !")

    def afficher_notification(self, titre: str, texte: str, duree: int = 1800) -> None:
        """Affiche une petite fenêtre comme un messagebox, mais sans bouton OK."""
        popup: tk.Toplevel = tk.Toplevel(self.racine)
        popup.title(titre)
        popup.resizable(False, False)
        popup.transient(self.racine)

        tk.Label(
            popup,
            text=texte,
            padx=25,
            pady=18,
            font=("Arial", 10),
        ).pack()

        popup.update_idletasks()
        x: int = self.racine.winfo_x() + (self.racine.winfo_width() // 2) - (popup.winfo_width() // 2)
        y: int = self.racine.winfo_y() + (self.racine.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        popup.after(duree, popup.destroy)

    def run(self) -> None:
        self.racine.mainloop()


if __name__ == "__main__":
    Controle().run()

