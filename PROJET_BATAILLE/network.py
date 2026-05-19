"""
PROJET : BATAILLE NAVALE
Module : network.py
Description : Gestion de la communication par socket (Serveur/Client).
Fait par : Hélène le 10.05.2026
"""

from __future__ import annotations
import socket
import threading
from tkinter import messagebox
from typing import Callable

# Type pour la fonction de rappel lors de la réception
CALLBACK_MESSAGE = Callable[[str], None]


class Connexion:
    """
    Gère la connexion réseau entre deux instances de jeu.
    
    Cette classe permet soit de créer un serveur pour attendre un adversaire,
    soit de se connecter à un serveur existant en tant que client.
    """
    
    def __init__(self) -> None:
        """
        Initialise le socket de base et prépare les variables d'état.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connexion = None
        self.host = None

    def serveur(self, port: int) -> None:
        """
        Démarre un serveur local pour attendre une connexion.

        Args:
            port (int): Le numéro de port sur lequel écouter.
        """
        # Récupération de l'adresse IP locale de la machine
        self.host = socket.gethostbyname(socket.gethostname())
        self.server.bind((self.host, port))
        self.server.listen(1)
        messagebox.showinfo("Connexion",
                            f"En attente de connexion...\nAdresse hôte : {self.host}")
        # Bloque l'exécution jusqu'à ce qu'un client se connecte
        self.connexion, adresse = self.server.accept()
        messagebox.showinfo("Connexion",
                            f"Connexion réussie avec {adresse[0]}")
        messagebox.showinfo("Début", "Commencez à placer vos bateaux")

    def client(self, host_adresse: str, port: int) -> None:
        """
        Se connecte à un serveur de jeu distant.

        Args:
            host_adresse (str): L'adresse IP du serveur (l'autre joueur).
            port (int): Le port de connexion.
        """
        self.server.connect((host_adresse, port))
        self.connexion = self.server
        messagebox.showinfo("Connexion", "Connexion réussie")

    def envoyer(self, msg: str) -> None:
        """
        Envoie un message texte à l'adversaire.

        Args:
            msg (str): Le message à envoyer (sera encodé en UTF-8).
        """
        if self.connexion is not None:
            self.connexion.send(msg.encode())

    def ecouter(self, callback: CALLBACK_MESSAGE) -> None:
        """
        Lance une boucle d'écoute dans un thread séparé pour recevoir
        les messages.

        Args:
            callback (CALLBACK_MESSAGE): Fonction à appeler
            quand un message arrive.
        """
        
        def boucle_ecoute() -> None:
            """Fonction interne exécutée en arrière-plan."""
            while True:
                try:
                    if self.connexion is None:
                        break

                    message: str = self.connexion.recv(1024).decode()
                    if message:
                        callback(message)
                    else:
                        break
                except OSError:
                    break

        if self.connexion is not None:
            #permet de faire fonctionner le programme en parrallèle
            thread = threading.Thread(target=boucle_ecoute, daemon=True)
            thread.start()

