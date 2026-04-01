import socket
import cadrillage as cd

HOST_ADRESS = "10.134.54.108"
PORT = 9999

class Ecouter:
    def __init__(self,host,port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host,port))
        
    def envoyer(self,bateaux):
        self.client.send(texte.encode())
        print(self.client.recv(1024).decode())
        self.client.send(bateaux)
        
    
if __name__ == "__main__":
    ecoute = Ecouter(HOST_ADRESS,PORT)
    ecoute.envoyer(vue.self.joueur_bateaux)
    controleur = cd.Controleur()
    vue = cd.Vue(controleur)
    controleur.lier_vue(vue)
    vue.lancer()
