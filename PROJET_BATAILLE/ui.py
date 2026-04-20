import tkinter as tk

class BatailleUI:
    def __init__(self, root, cb_tir, cb_place):
        self.root = root
        self.bt_moi, self.bt_adv = {}, {}
        f1 = tk.Frame(root); f1.pack(side=tk.LEFT, padx=20, pady=20)
        f2 = tk.Frame(root); f2.pack(side=tk.RIGHT, padx=20, pady=20)
        tk.Label(f1, text="MA FLOTTE", font=('Arial', 10, 'bold')).grid(row=0, column=1, columnspan=10)
        tk.Label(f2, text="ATTAQUE", font=('Arial', 10, 'bold')).grid(row=0, column=1, columnspan=10)
        for l in range(1, 11):
            for c in range(1, 11):
                b_m = tk.Button(f1, width=3, bg="#E1F5FE", command=lambda l=l,c=c: cb_place(l,c))
                b_m.grid(row=l, column=c); self.bt_moi[(l,c)] = b_m
                b_a = tk.Button(f2, width=3, bg="#ECEFF1", command=lambda l=l,c=c: cb_tir(l,c))
                b_a.grid(row=l, column=c); self.bt_adv[(l,c)] = b_a

    def colorier(self, grille, l, c, couleur):
        target = self.bt_moi if grille == "moi" else self.bt_adv
        if (l,c) in target: target[(l,c)].config(bg=couleur)
    
    def set_titre(self, texte):
        self.root.title(f"Bataille Navale - {texte}")