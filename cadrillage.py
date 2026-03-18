import tkinter as tk
from tkinter import messagebox
import random

TAILLE_CASE = 40
NB_LIGNES = 11
NB_COLONNES = 11
ESPACE = 100
DECALAGE_BAS = 80

lettres = ["A","B","C","D","E","F","G","H","I","J"]
chiffres = [1,2,3,4,5,6,7,8,9,10]


# ======== CONTROLEUR =====
class Controleur:

    def __init__(self):

        self.vue = None
        self.phase = "placement"

        self.bateau_taille_actuelle = 1
        self.bateaux_a_placer = [1,2,3,4,5]

        self.joueur_bateaux = []
        self.adversaire_bateaux = []

        self.bateau_en_cours = []
        self.orientation = None

        self.tirs = set()
        self.coups = 0


    def lier_vue(self, vue):
        self.vue = vue
        self.generer_bateaux_adversaire()


# ------------------------
# Placement bateaux joueur
# ------------------------

    def placer_bateau(self, ligne, colonne):

        if self.phase != "placement":
            return

        if (ligne,colonne) in self.bateau_en_cours:
            messagebox.showinfo("Erreur","Case déjà choisie")
            return

        for bateau in self.joueur_bateaux:
            if (ligne,colonne) in bateau:
                messagebox.showinfo("Erreur","Case déjà occupée")
                return

        # Définition orientation
        if len(self.bateau_en_cours) == 1:

            l0,c0 = self.bateau_en_cours[0]

            if ligne == l0:
                self.orientation = "H"

            elif colonne == c0:
                self.orientation = "V"

            else:
                messagebox.showinfo("Erreur","Le bateau doit être horizontal ou vertical")
                return

        # Vérification orientation
        if len(self.bateau_en_cours) >= 1:

            l0,c0 = self.bateau_en_cours[0]

            if self.orientation == "H" and ligne != l0:
                messagebox.showinfo("Erreur","Le bateau doit rester horizontal")
                return

            if self.orientation == "V" and colonne != c0:
                messagebox.showinfo("Erreur","Le bateau doit rester vertical")
                return

        # ✅ NOUVEAU : vérifier que la case est adjacente
        if len(self.bateau_en_cours) >= 1:

            adjacent = False

            for (l, c) in self.bateau_en_cours:

                if (ligne == l and abs(colonne - c) == 1) or \
                   (colonne == c and abs(ligne - l) == 1):

                    adjacent = True

            if not adjacent:
                messagebox.showinfo("Erreur", "Les cases doivent être collées")
                return

        # Ajout de la case
        self.bateau_en_cours.append((ligne,colonne))
        self.vue.marquer_case_joueur(ligne,colonne,"gray")

        taille = self.bateau_taille_actuelle

        if len(self.bateau_en_cours) == taille:

            self.joueur_bateaux.append(self.bateau_en_cours.copy())

            self.bateau_en_cours.clear()
            self.orientation = None

            self.bateaux_a_placer.remove(taille)

            if self.bateaux_a_placer:

                self.bateau_taille_actuelle = self.bateaux_a_placer[0]

                messagebox.showinfo(
                    "Placement",
                    f"Bateau placé !\nPlacez un bateau de taille {self.bateau_taille_actuelle}"
                )

            else:

                self.phase = "jeu"

                messagebox.showinfo(
                    "Jeu",
                    "Tous les bateaux sont placés !\nCommencez à tirer."
                )


# ------------------------
# Génération bateaux IA
# ------------------------

    def generer_bateaux_adversaire(self):

        tailles = [1,2,3,4,5]
        bateaux = []

        for taille in tailles:

            place = False

            while not place:

                orientation = random.choice(["H","V"])
                ligne = random.randint(1,10)
                colonne = random.randint(1,10)

                positions = []

                for i in range(taille):

                    if orientation == "H":
                        pos = (ligne, colonne+i)
                    else:
                        pos = (ligne+i, colonne)

                    if pos[0] > 10 or pos[1] > 10:
                        break

                    positions.append(pos)

                collision = False

                for p in positions:
                    for bateau in bateaux:
                        if p in bateau:
                            collision = True

                if len(positions) == taille and not collision:
                    bateaux.append(positions)
                    place = True

        self.adversaire_bateaux = bateaux


# ------------------------
# Tir
# ------------------------

    def tirer(self, ligne, colonne):

        if self.phase != "jeu":
            messagebox.showinfo("Info","Placez vos bateaux d'abord")
            return

        if (ligne,colonne) in self.tirs:
            messagebox.showinfo("Info","Vous avez déjà tiré ici")
            return

        self.tirs.add((ligne,colonne))
        self.coups += 1

        touche = False

        for bateau in self.adversaire_bateaux:

            if (ligne,colonne) in bateau:

                touche = True
                self.vue.marquer_case_adversaire(ligne,colonne,"red")

                if all(pos in self.tirs for pos in bateau):
                    messagebox.showinfo("Bateau coulé","Vous avez coulé un bateau !")
                else:
                    messagebox.showinfo("Touché","Vous avez touché une partie du bateau !")

        if not touche:
            self.vue.marquer_case_adversaire(ligne,colonne,"white")

        toutes_positions = []

        for bateau in self.adversaire_bateaux:
            for pos in bateau:
                toutes_positions.append(pos)

        if all(pos in self.tirs for pos in toutes_positions):
            self.fin_partie()


# ------------------------
# Fin du jeu
# ------------------------

    def fin_partie(self):

        messagebox.showinfo(
            "Victoire",
            f"Bravo ! Vous avez gagné en {self.coups} coups."
        )


# ========== VUE ==========
class Vue:

    def __init__(self, controleur):

        self.controleur = controleur

        self.fenetre = tk.Tk()
        self.fenetre.title("Bataille Navale")

        self.boutons_joueur = {}
        self.boutons_adversaire = {}

        largeur_plateau = NB_COLONNES * TAILLE_CASE
        largeur_totale = largeur_plateau*2 + ESPACE + 100

        self.fenetre.geometry(f"{largeur_totale}x700")

        x1 = 50
        x2 = largeur_plateau + ESPACE

        tk.Label(self.fenetre,text="Ma grille",font=("Arial",16)).place(x=x1+150,y=20)
        tk.Label(self.fenetre,text="Grille adversaire",font=("Arial",16)).place(x=x2+150,y=20)

        self.dessiner_plateau(x1,DECALAGE_BAS,True)
        self.dessiner_plateau(x2,DECALAGE_BAS,False)

        messagebox.showinfo("Placement","Placez un bateau de taille 1")


    def dessiner_plateau(self,offset_x,offset_y,joueur):

        for ligne in range(NB_LIGNES):
            for colonne in range(NB_COLONNES):

                if ligne == 0 and colonne > 0:

                    tk.Label(self.fenetre,text=lettres[colonne-1],relief="solid").place(
                        x=colonne*TAILLE_CASE+offset_x,
                        y=ligne*TAILLE_CASE+offset_y,
                        width=TAILLE_CASE,
                        height=TAILLE_CASE
                    )

                elif colonne == 0 and ligne > 0:

                    tk.Label(self.fenetre,text=chiffres[ligne-1],relief="solid").place(
                        x=colonne*TAILLE_CASE+offset_x,
                        y=ligne*TAILLE_CASE+offset_y,
                        width=TAILLE_CASE,
                        height=TAILLE_CASE
                    )

                elif ligne > 0 and colonne > 0:

                    bouton = tk.Button(self.fenetre,bg="lightblue")

                    bouton.place(
                        x=colonne*TAILLE_CASE+offset_x,
                        y=ligne*TAILLE_CASE+offset_y,
                        width=TAILLE_CASE,
                        height=TAILLE_CASE
                    )

                    if joueur:

                        bouton.config(
                            command=lambda l=ligne,c=colonne:
                            self.controleur.placer_bateau(l,c)
                        )

                        self.boutons_joueur[(ligne,colonne)] = bouton

                    else:

                        bouton.config(
                            command=lambda l=ligne,c=colonne:
                            self.controleur.tirer(l,c)
                        )

                        self.boutons_adversaire[(ligne,colonne)] = bouton


    def marquer_case_joueur(self,ligne,colonne,couleur):
        self.boutons_joueur[(ligne,colonne)].config(bg=couleur)


    def marquer_case_adversaire(self,ligne,colonne,couleur):
        self.boutons_adversaire[(ligne,colonne)].config(bg=couleur)


    def lancer(self):
        self.fenetre.mainloop()


# ========= MAIN ==========
controleur = Controleur()
vue = Vue(controleur)

controleur.lier_vue(vue)

vue.lancer()
