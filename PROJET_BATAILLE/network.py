from __future__ import annotations

import socket
import threading
from tkinter import messagebox
from typing import Callable

CallbackMessage = Callable[[str], None]


class Connexion:
    def __init__(self) -> None:
        self.server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connexion: socket.socket | None = None
        self.host: str | None = None

    def serveur(self, port: int) -> None:
        self.host = socket.gethostbyname(socket.gethostname())
        self.server.bind((self.host, port))
        self.server.listen(1)
        messagebox.showinfo("Connexion", f"En attente de connexion...\nAdresse hôte : {self.host}")
        self.connexion, adresse = self.server.accept()
        messagebox.showinfo("Connexion", f"Connexion réussie avec {adresse[0]}")
        messagebox.showinfo("Début", "Commencez à placer vos bateaux")

    def client(self, host_adresse: str, port: int) -> None:
        self.server.connect((host_adresse, port))
        self.connexion = self.server
        messagebox.showinfo("Connexion", "Connexion réussie")

    def envoyer(self, msg: str) -> None:
        if self.connexion is not None:
            self.connexion.send(msg.encode())

    def ecouter(self, callback: CallbackMessage) -> None:
        def boucle_ecoute() -> None:
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
            thread: threading.Thread = threading.Thread(target=boucle_ecoute, daemon=True)
            thread.start()

