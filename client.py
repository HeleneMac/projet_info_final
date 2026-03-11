"""qd on host on utilise l'adresse privée, qd on se connect, on utilise l'adresse publique"""
import socket

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
HOST_ADRESS = "10.134.53.56"
HOST = "127.0.0.1"
PORT = 9999
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
SERVER_IP = '192.168.1.XX'
# REMPLACEZ par l'IP réelle du serveur notée à l'étape 1
#client.connect((HOST,PORT))
client.connect((HOST_ADRESS,PORT))

client.send("Salut de l'autre ordi !".encode())
#-->il faut réencoder le message
print(client.recv(1024).decode())
# --> sinon on aura le message en bitsclient.close()

#client.close()