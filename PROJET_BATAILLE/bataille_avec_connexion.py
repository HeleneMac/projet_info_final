import socket
import threading
from tkinter import messagebox

class Connexion:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connexion = None
        self.host = None

    def serveur(self, port):
        self.host = socket.gethostbyname(socket.gethostname())
        self.server.bind((self.host, port))
        self.server.listen(1)
        messagebox.showinfo("Connexion", f"En attente de connexion...\nAdresse hôte : {self.host}")
        self.connexion, adresse = self.server.accept()
        messagebox.showinfo("Connexion", f"Connexion réussie avec {adresse[0]}")

    def client(self, host_adresse, port):
        self.server.connect((host_adresse, port))
        self.connexion = self.server
        messagebox.showinfo("Connexion", "Connexion réussie")

    def envoyer(self, msg):
        if self.connexion is not None:
            self.connexion.send(msg.encode())

    def ecouter(self, callback):
        def boucle_ecoute():
            while True:
                try:
                    message = self.connexion.recv(1024).decode()
                    if message:
                        callback(message)
                    else:
                        break
                except:
                    break

        if self.connexion is not None:
            thread = threading.Thread(target=boucle_ecoute, daemon=True)
            thread.start()
