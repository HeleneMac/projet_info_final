import tkinter as tk

class BatailleUI:
    """Interface graphique du jeu Bataille Navale.
    Affiche les grilles du joueur et de l'adversaire."""
      
    def __init__(self, root, callback_tir, callback_placement):
        """
            Initialise la fenêtre du jeu et crée les grilles.

            Args:
                root (tk.Tk): fenêtre principale
                callback_tir (function): fonction appelée lors d'un tir
                callback_placement (function): fonction appelée lors du placement des bateaux
        """
    
        self.root = root
        self.boutons_ma_flotte[(ligne, colonne)] = bouton_flotte
        self.bateau_adversaire = {}
        
        frame_flotte = tk.Frame(root)
        frame_flotte.pack(side=tk.LEFT, padx=20, pady=20)
        
        frame_adversaire = tk.Frame(root)
        frame_adversaire.pack(side=tk.RIGHT, padx=20, pady=20)
        
        tk.Label(frame_flotte, text="MA FLOTTE", font=('Arial', 10, 'bold')).grid(row=0, column=1, columnspan=10)
        tk.Label(frame_adversaire, text="ATTAQUE", font=('Arial', 10, 'bold')).grid(row=0, column=1, columnspan=10)
        
        for ligne in range(1, 11):
            for colonne in range(1, 11):
                
                bouton_flotte = tk.Button(
                    frame_flotte,
                    width=3,
                    bg="#E1F5FE",
                    command=lambda ligne=ligne,colonne=colonne: callback_placement(ligne,colonne)
                )
                
                bouton_flotte.grid(row=ligne, column=colonne)
                self.bateau_moi[(ligne,colonne)] = bouton_flotte
                
                
                bouton_adversaire = tk.Button(
                    frame_adversaire,
                    width=3,
                    bg="#ECEFF1",
                    command=lambda ligne=ligne,colonne=colonne: callback_tir(ligne,colonne)
                )
                
                bouton_adversaire.grid(row=ligne, column=colonne)
                self.bateau_adversaire[(ligne,colonne)] = bouton_adversaire

    def colorier(self, grille, ligne, colonne, couleur):
        """
        Change la couleur d'une case sur une grille.

        Args:
            grille (str): "moi" ou "adversaire"
            ligne (int): ligne de la case
            colonne (int): colonne de la case
            couleur (str): couleur Tkinter (ex: "red", "blue")
        """
        
        if grille == "moi":
            target = self.boutons_ma_flotte
        else:
            target = self.bateau_adversaire
            
        if (ligne,colonne) in target:
            target[(ligne,colonne)].config(bg=couleur)
    
    def set_titre(self, texte):
        """
        Modifie le titre de la fenêtre.

        Args:
            texte (str): texte à afficher dans le titre
        """
            
        self.root.title(f"Bataille Navale - {texte}")