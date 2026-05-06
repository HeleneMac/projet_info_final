import socket
import threading

class Connexion:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connexion = None
        self.host = None

    def serveur(self,port):
        self.host = socket.gethostbyname(socket.gethostname())
        self.server.bind((self.host,port))
        self.server.listen(1)
        messagebox.showinfo("Conexion","En attente de connexion...")
        (self.connexion, adresse) = self.server.accept()
        messagebox.showinfo("Connexion","Connexion réussie")

    def client(self, host_adress,port):
        self.server.connect((host_adresse,port))
        self.connexion = self.server
        messagebox.showinfo("Connexion","Connexion réussie")

    def envoyer(self, msg):
        self.connexion.send(msg.encode())

    def ecouter(self, callback):
        def boucle_ecoute():
            while True:
                try:
                    message = self.connexion.recv(1024).decode()
                    if message:
                        callback(message)
                except:
                    break

        thread = threading.Thread(target=boucle_ecoute, daemon=True)#permet de faire fonctionner le programme en parrallèle
        thread.start()
