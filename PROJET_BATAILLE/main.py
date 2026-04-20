"""
Module : main.py
Contrôleur principal avec guidage réseau pas à pas.
"""
import tkinter as tk
from tkinter import messagebox
import random
from engine import BatailleEngine
from network import NetworkManager
from ui import BatailleUI

class GameController:
    def __init__(self):
        self.root = tk.Tk()
        self.engine = BatailleEngine()
        self.net = NetworkManager()
        self.ui = BatailleUI(self.root, self.on_tir, self.on_place)
        self.pret_moi, self.pret_adv, self.mon_tour = False, False, False
        self.mode = None
        self.tirs_ia = set()
        self.config_initiale()

    def config_initiale(self):
        print("\n" + "="*40)
        print(" BIENVENUE DANS LA BATAILLE NAVALE")
        print("="*40)
        choix = input("1: Solo vs Ordinateur | 2: Multi-joueurs : ")
        
        if choix == '1':
            self.mode = "SOLO"; self.pret_adv = True
            self.engine_ia = BatailleEngine()
            self.engine_ia.placer_bateaux_aleatoire()
            self.mon_tour = True
            messagebox.showinfo("Placer bateaux", "Mode Solo : Placez vos bateaux !")
        else:
            self.mode = "MULTI"
            role = input("Êtes-vous Serveur (s) ou Client (c) ? : ").lower()
            if role == 's':
                print("\n--- INSTRUCTIONS POUR TROUVER VOTRE IP ---")
                print("1. Appuyez sur les touches [Windows] + [R]")
                print("2. Tapez 'cmd' et appuyez sur Entrée")
                print("3. Dans la fenêtre noire, tapez 'ipconfig'")
                print("4. Cherchez la ligne 'Adresse IPv4' (ex: 192.168.X.X)")
                print("------------------------------------------")
                print("En attente de votre partenaire...")
                self.net.start_as_server()
                self.mon_tour = True
            else:
                print("\n--- INSTRUCTIONS CONNEXION ---")
                print("Demandez l'adresse IPv4 à votre partenaire.")
                print("Elle doit ressembler à ceci : 000.000.000.000")
                ip = input("Entrez l'adresse IP du serveur : ")
                self.net.start_as_client(ip)
            self.net.ecouter(self.handle_data)
            messagebox.showinfo("Placer bateaux", "Connecté ! Placez vos bateaux !")

    def on_place(self, l, c):
        if self.pret_moi: return
        valide, msg = self.engine.valider_clic(l, c)
        if not valide:
            messagebox.showwarning("Attention", msg); return

        fini = self.engine.ajouter_point(l, c)
        self.ui.colorier("moi", l, c, "blue")

        if fini:
            if self.engine.index_taille < len(self.engine.tailles_a_placer):
                t = self.engine.tailles_a_placer[self.engine.index_taille]
                messagebox.showinfo("Suivant", f"Bateau terminé. Placez le suivant (taille {t})")
            else:
                self.pret_moi = True
                if self.mode == "MULTI": self.net.envoyer("READY")
                self.verifier_demarrage()

    def verifier_demarrage(self):
        if self.pret_moi and self.pret_adv:
            self.ui.set_titre("À VOUS DE JOUER" if self.mon_tour else "ATTENTE ADVERSAIRE")
            messagebox.showinfo("Début", "Tout le monde est prêt ! Attaquez !")
        elif self.pret_moi:
            self.ui.set_titre("ATTENTE ADVERSAIRE")
            messagebox.showinfo("Attente", "Vous avez fini ! On attend l'adversaire.")

    def on_tir(self, l, c):
        if not self.pret_moi or not self.pret_adv:
            messagebox.showwarning("Attente", "Le placement n'est pas fini !"); return
        if not self.mon_tour:
            messagebox.showinfo("Tour", "C'est le tour de l'adversaire !"); return

        if self.mode == "SOLO":
            res = self.engine_ia.verifier_tir(l, c)
            self.traiter_resultat_tir("adv", l, c, res)
            self.mon_tour = False; self.root.after(800, self.faire_jouer_ia)
        else:
            self.net.envoyer(f"TIR:{l},{c}")
            self.mon_tour = False
            self.ui.set_titre("ATTENTE ADVERSAIRE...")

    def handle_data(self, data):
        if data == "READY":
            self.pret_adv = True
            self.root.after(0, self.verifier_demarrage)
        elif data.startswith("TIR:"):
            l, c = map(int, data.split(":")[1].split(","))
            res = self.engine.verifier_tir(l, c)
            self.ui.colorier("moi", l, c, "red" if res in ["TOUCHÉ", "COULÉ"] else "black")
            self.net.envoyer(f"RES:{l},{c},{res}")
            self.mon_tour = True
            self.ui.set_titre("À VOUS DE JOUER !")
            messagebox.showinfo("Alerte", f"L'adversaire a tiré en {l},{c} : {res} !")
        elif data.startswith("RES:"):
            l, c, res = data.split(":")[1].split(",")
            self.traiter_resultat_tir("adv", int(l), int(c), res)

    def traiter_resultat_tir(self, grille, l, c, res):
        if res == "DÉJÀ TIRÉ":
            messagebox.showinfo("Info", "Déjà tiré ici !"); self.mon_tour = True; return
        self.ui.colorier(grille, l, c, "red" if res in ["TOUCHÉ", "COULÉ"] else "black")
        messagebox.showinfo("Résultat", f"Tir en {l},{c} : {res}")
        if self.mode == "MULTI" and not self.mon_tour: self.ui.set_titre("TOUR ADVERSAIRE")

    def faire_jouer_ia(self):
        l, c = random.randint(1, 10), random.randint(1, 10)
        while (l, c) in self.tirs_ia: l, c = random.randint(1, 10), random.randint(1, 10)
        self.tirs_ia.add((l, c))
        res = self.engine.verifier_tir(l, c)
        self.ui.colorier("moi", l, c, "red" if res in ["TOUCHÉ", "COULÉ"] else "black")
        self.mon_tour = True
        self.ui.set_titre("À VOUS DE JOUER !")

    def run(self): self.root.mainloop()

if __name__ == "__main__":
    GameController().run()