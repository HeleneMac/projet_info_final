import socket

HOST_ADRESS = "10.134.54.108"
PORT = 9999

class Ecouter:
    def __init__(self,host,port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host,port))
        
    def envoyer(self,texte):
        self.client.send(texte.encode())
        print(self.client.recv(1024).decode())
        
    
if __name__ == "__main__":
    ecoute = Ecouter(HOST_ADRESS,PORT)
    ecoute.envoyer("salut du client")
