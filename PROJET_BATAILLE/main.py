"""
PROJET : BATAILLE NAVALE
Module : main.py
Description : Contrôleur principal orchestrant la logique de jeu, les tours et le réseau.
Fait par Hélène, Bianca et Christina
"""

from __future__ import annotations
import random
import tkinter as tk
from tkinter import messagebox
from typing import Literal

from engine import BatailleEngine, RESULTAT_TIR
from network import Connexion
from ui import BatailleUI, GRILLE

PORT_SERVEUR: int = 9999
MODE_JEU = Literal["SOLO", "MULTI"]
POSITION = tuple[int, int]


class Controle:
    """
    Classe pivot (Contrôleur) gérant les interactions entre l'utilisateur et le moteur.
    
    Attributes:
        racine (tk.Tk): Fenêtre principale.
        engine (BatailleEngine): Moteur pour la grille du joueur.
        engine_ia (BatailleEngine): Moteur pour la grille adverse (en mode Solo).
        net (Connexion): Gestionnaire de communication réseau.
        ui (BatailleUI): Gestionnaire de l'interface graphique.
    """
    
    def __init__(self) -> None:
        """Initialise les composants du jeu et prépare l'écran d'accueil."""
        self.racine: tk.Tk = tk.Tk()
        self.engine: BatailleEngine = BatailleEngine()
        self.engine_ia: BatailleEngine | None = None
        self.net: Connexion = Connexion()
        self.ui: BatailleUI = BatailleUI(self.racine, self.on_tir, self.on_place)

        self.pret_moi: bool = False
        self.pret_adv: bool = False
        self.mon_tour: bool = False
        self.mode: MODE_JEU | None = None
        self.tirs_ordi: set[POSITION] = set()
        self.tirs_joueur: set[POSITION] = set()

        self.texte: tk.Label = tk.Label(self.racine, text="Adresse de l'hôte:", font=30)
        self.host_adresse: tk.Entry = tk.Entry(self.racine)
        self.bouton_connexion: tk.Button = tk.Button(
            self.racine,
            text="Connexion",
            command=self.connecter_client,
        )

        self.config_initiale()

    def config_initiale(self) -> None:
        """Détermine le mode de jeu et initialise les serveurs ou la version contre l'ordinateur."""
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
                self.net.serveur(PORT_SERVEUR)
                self.net.ecouter(self.handle_data)
                self.mon_tour = True
            else:
                messagebox.showinfo("Connexion", "Entrez l'adresse de l'hôte")
                self.texte.pack(pady=2)
                self.host_adresse.pack(pady=2)
                self.bouton_connexion.pack(pady=5)

    def connecter_client(self) -> None:
        """Établit la connexion avec l'hôte et retire les champs de saisie."""
        self.net.client(self.host_adresse.get(), PORT_SERVEUR)
        self.net.ecouter(self.handle_data)
        messagebox.showinfo("Placer bateaux", "Connecté ! Placez vos bateaux !")

    def on_place(self, ligne: int, colonne: int) -> None:
        """
        Gère le clic sur la grille 'Moi' pour placer les bateaux.

        Args:
            ligne (int): Ligne cliquée.
            colonne (int): Colonne cliquée.
        """
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
            """Vérifie si la phase d'attaque peut commencer."""
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
        """
        Gère la tentative de tir sur la grille adverse.

        Args:
            ligne, colonne: Coordonnées de la cible.
        """
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
        """
        Analyse les messages reçus par le réseau et déclenche les actions.

        Args:
            data (str): Message brut reçu du socket.
        """
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
            #self.afficher_notification("Alerte", f"L'adversaire a tiré en {ligne},{colonne} : {resultat} !")
        
        elif data.startswith("RES:"):
            ligne_str: str
            colonne_str: str
            resultat_str: str
            ligne_str, colonne_str, resultat_str = data.split(":")[1].split(",")
            self.traiter_resultat_tir("adversaire", int(ligne_str), int(colonne_str), resultat_str)
            if resultat_str == "COULÉ":
                self.net.envoyer("CHECK_WIN")
    
        elif data == "CHECK_WIN":
            if self.engine.tous_coules():
                self.net.envoyer("YOU_WIN")
    
        elif data == "YOU_WIN":
            self.racine.after(0, lambda: self.fin("Vous avez"))

    def traiter_resultat_tir(self, grille: Grille, ligne: int, colonne: int, resultat: str) -> None:
        """Met à jour l'UI après un résultat de tir et vérifie la victoire en solo."""
        if resultat == "DÉJÀ TIRÉ":
            self.afficher_notification("Déjà tiré", "Déjà tiré sur cette case, choisissez une autre case.")
            self.mon_tour = True
            self.ui.set_titre("À VOUS DE JOUER !")
            return

        self.ui.colorier(grille, ligne, colonne, "red" if resultat in ["TOUCHÉ", "COULÉ"] else "black")
        if resultat == "COULÉ":
            self.afficher_notification("Résultat", f"Bateau {resultat}!!!")
            
        
        if self.mode == "SOLO" and resultat == "COULÉ":
            if self.engine_ia is not None and self.engine_ia.tous_coules():
                self.racine.after(500, lambda: self.fin("Vous avez"))
                return
        
        if self.mode == "MULTI" and not self.mon_tour:
            self.ui.set_titre("TOUR ADVERSAIRE")

    def faire_jouer_ordi(self) -> None:
        """Simule un tir aléatoire de l'intelligence artificielle."""
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
        
        if resultat == "COULÉ" and self.engine.tous_coules():
            self.racine.after(500, lambda: self.fin("Ordinateur a"))
            return
        if resultat == "COULÉ":
            self.afficher_notification("Résultat", f"Bateau {resultat}!!!")
        self.mon_tour = True
        self.ui.set_titre("À VOUS DE JOUER !")

    def afficher_notification(self, titre: str, texte: str, duree: int = 1800) -> None:
        """Affiche un popup temporaire au centre de l'écran."""
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
        
    def fin(self, gagnant: str) -> None:
        """Affiche le message de fin et ferme l'application."""
        if self.mode == "MULTI":
            self.net.envoyer(f"FIN:{gagnant}")
        messagebox.showinfo("Fin de partie", f" {gagnant} gagné la partie !")#ici gagnant doit être soit vous soit adversaire ou prénom
        self.racine.destroy()
            
    
    def run(self) -> None:
        """Démarre l'application."""
        self.racine.mainloop()


if __name__ == "__main__":
    Controle().run()

