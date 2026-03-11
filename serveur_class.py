import socket


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
        
    def envoyer(self,client,text):
        client.send(text.encode())
        print(client.recv(1024).decode())
        
        
if __name__ == "__main__":
    connect = Connexion(PORT)
    client = connect.ecoute()
    connect.envoyer(client,"salut de l'host")
    client.close()

