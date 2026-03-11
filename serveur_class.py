import socket


HOST_ADRESS = "10.134.53.56"
PORT = 9999



class Connexion:
    def __init__(self,host,port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(1)
        
    def ecoute(self):
            (client,adresse) = self.server.accept()
            return client
        
    def envoyer(self,client,text):
        client.send(text.encode())
        print(client.recv(1024).decode())
        
        
if __name__ == "__main__":
    connect = Connexion(HOST_ADRESS,PORT)
    client = connect.ecoute()
    connect.envoyer(client,"salut de l'host")
    client.close()

