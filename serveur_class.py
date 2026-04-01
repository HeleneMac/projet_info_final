import socket
import cadrillage as cd


#HOST_ADRESS = "10.134.54.108"
PORT = 9999

class Connexion:
    def __init__(self,port):
        self.host = socket.gethostbyname(socket.gethostname())
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, port))
        self.server.listen(1)
        
    def ecoute(self):
            print("en attente...")
            (client,adresse) = self.server.accept()
            return client
        
    def envoyer(self,client,bateaux):
        client.send("salut".encode())
        print(client.recv(1024).decode())
        client.send(bateaux)
        
        
        
        
if __name__ == "__main__":
    controleur = cd.Controleur()
    vue = cd.Vue(controleur)
    controleur.lier_vue(vue)
    vue.lancer()
    connect = Connexion(PORT)
    client = connect.ecoute()
    connect.envoyer(client,vue.self.joueur_bateaux)
    client.close()
    