import socket
import threading

class NetworkManager:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None

    def start_as_server(self):
        self.sock.bind(('0.0.0.0', 5555))
        self.sock.listen(1)
        self.conn, _ = self.sock.accept()

    def start_as_client(self, ip):
        self.sock.connect((ip, 5555))
        self.conn = self.sock

    def envoyer(self, msg):
        if self.conn: self.conn.send(msg.encode())

    def ecouter(self, callback):
        def loop():
            while True:
                try:
                    data = self.conn.recv(1024).decode()
                    if data: callback(data)
                except: break
        threading.Thread(target=loop, daemon=True).start()