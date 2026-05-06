"""
Module : main.py
Contrôleur principal avec guidage réseau pas à pas.
"""
import tkinter as tk
from tkinter import messagebox
import random
from engine import BatailleEngine
from network import Connexion
from ui import BatailleUI

PORT = 9999

class Controle:
    def __init__(self):
        self.racine = tk.Tk()
        self.engine = BatailleEngine()
        self.net = Connexion()
        self.ui = BatailleUI(self.racine, self.on_tir, self.on_place)
        self.pret_moi = False
        self.pret_adv = False
        self.mon_tour = False
        self.mode = None
        self.tirs_ordi = set()

        self.texte = tk.Label(self.racine, text="Adresse de l'hôte:", font=30)
        self.host_adresse = tk.Entry(self.racine)
        self.bouton_connexion = tk.Button(
            self.racine,
            text="Connexion",
            command=self.connecter_client
        )

        self.config_initiale()

    def config_initiale(self):
        """Permet de choisir le mode et de connecter au besoin selon si l'ordi est hôte ou client."""
        print("\n" + "=" * 40)
        print(" BIENVENUE DANS LA BATAILLE NAVALE")
        print("=" * 40)

        choix = messagebox.askyesno("Seul/Multijoueur", "Jouez-vous seul ?")
        
        if choix:
            self.mode = "SOLO"
            self.pret_adv = True
            self.engine_ia = BatailleEngine()
            self.engine_ia.placer_bateaux_aleatoire()
            self.mon_tour = True
            messagebox.showinfo("Placer bateaux", "Mode Solo : Placez vos bateaux !")
        else:
            self.mode = "MULTI"
            role = messagebox.askyesno("Client/Serveur", "Êtes-vous l'hôte ?")
            if role:
                self.net.serveur(PORT)
                self.net.ecouter(self.handle_data)
                self.mon_tour = True
            else:
                messagebox.showinfo("Connexion","Entrez l'adresse de l'hôte en haut à gauche")
                self.texte.place(x=5, y=5)
                self.host_adresse.place(x=135, y=5)
                self.bouton_connexion.place(x=260, y=3)
            messagebox.showinfo("Début","Vous pouvez commencer à placer vos bateaux")
                
        

    def connecter_client(self):
        """Connecte le client puis démarre l'écoute réseau."""
        self.net.client(self.host_adresse.get(), PORT)
        self.net.ecouter(self.handle_data)
        messagebox.showinfo("Placer bateaux", "Connecté ! Placez vos bateaux !")

    def on_place(self, ligne, colonne):
        """Place les bateaux tant que le joueur n'est pas prêt."""
        if self.pret_moi:
            return

        valide, msg = self.engine.valider_clic(ligne, colonne)

        if not valide:
            messagebox.showwarning("Attention", msg)
            return

        fini = self.engine.ajouter_point(ligne, colonne)
        self.ui.colorier("moi", ligne, colonne, "blue")

        if fini:
            if self.engine.index_taille < len(self.engine.tailles_a_placer):
                taille = self.engine.tailles_a_placer[self.engine.index_taille]
                messagebox.showinfo("Suivant", f"Bateau terminé. Placez le suivant (taille {taille})")
            else:
                self.pret_moi = True
                if self.mode == "MULTI":
                    self.net.envoyer("READY")
                self.verifier_demarrage()

    def verifier_demarrage(self):
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
        
    def on_tir(self, ligne, colonne):
        """Gère un tir du joueur."""
        if not self.pret_moi or not self.pret_adv:
            messagebox.showwarning("Attente", "Le placement n'est pas fini !")
            return

        if not self.mon_tour:
            messagebox.showinfo("Tour", "C'est le tour de l'adversaire !")
            return

        if self.mode == "SOLO":
            resultat = self.engine_ia.verifier_tir(ligne, colonne)
            self.traiter_resultat_tir("adversaire", ligne, colonne, resultat)
            self.mon_tour = False
            self.racine.after(800, self.faire_jouer_ordi)
        else:
            self.net.envoyer(f"TIR:{ligne},{colonne}")
            self.mon_tour = False
            self.ui.set_titre("ATTENTE ADVERSAIRE...")
    
    def handle_data(self, data):
        if data == "READY":
            self.pret_adv = True
            self.racine.after(0, self.verifier_demarrage)
        elif data.startswith("TIR:"):
            ligne, colonne = map(int, data.split(":")[1].split(","))
            resultat = self.engine.verifier_tir(ligne, colonne)
            if resultat in ["TOUCHÉ", "COULÉ"]:
                self.ui.colorier("moi", ligne, colonne, "red")
            else:
                self.ui.colorier("moi", ligne, colonne, "black")
            self.net.envoyer(f"RES:{ligne},{colonne},{resultat}")
            self.mon_tour = True
            self.ui.set_titre("À VOUS DE JOUER !")
            messagebox.showinfo("Alerte", f"L'adversaire a tiré en {ligne},{colonne} : {resultat} !")
        elif data.startswith("RES:"):
            ligne, colonne, resultat = data.split(":")[1].split(",")
            self.traiter_resultat_tir("adversaire", int(ligne), int(colonne), resultat)

    def traiter_resultat_tir(self, grille, ligne, colonne, resultat):
        if resultat == "DÉJÀ TIRÉ":
            messagebox.showinfo("Info", "Déjà tiré ici !")
            self.mon_tour = True
            return
        self.ui.colorier(grille, ligne, colonne, "red" if resultat in ["TOUCHÉ", "COULÉ"] else "black")
        messagebox.showinfo("Résultat", f"Tir en {ligne},{colonne} : {resultat}")
        if self.mode == "MULTI" and not self.mon_tour:
            self.ui.set_titre("TOUR ADVERSAIRE")

    def faire_jouer_ordi(self):
        ligne, colonne = random.randint(1, 10), random.randint(1, 10)
        while (ligne, colonne) in self.tirs_ordi:
            ligne, colonne = random.randint(1, 10), random.randint(1, 10)
        self.tirs_ordi.add((ligne, colonne))
        resultat = self.engine.verifier_tir(ligne, colonne)
        if resultat in ["TOUCHÉ", "COULÉ"]:
            self.ui.colorier("moi", ligne, colonne, "red")
        else:
            self.ui.colorier("moi", ligne, colonne, "black")
        messagebox.showinfo("Tour ordinateur", f"L'ordinateur a tiré en {ligne},{colonne} : {resultat}")
        self.mon_tour = True
        self.ui.set_titre("À VOUS DE JOUER !")

    def run(self):
        self.racine.mainloop()

if __name__ == "__main__":
    Controle().run()
