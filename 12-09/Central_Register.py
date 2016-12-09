import socket
import startupBBB

IP = IP
UDP_PORT = PORT

sock = socket.socket(socket.AF_INT, socket.SOCK_DGRAM)
sock.bind((self.IP, self.UDP_PORT))

#startupBBB.cleandir() # clean directory from '.pem' and '.pickle' files



clients = [] # list of (id, (ip, port), publik_key(exported version))

while True:
    
    data, addr = sock.recvfrom(2048)
    
    if clients.contains(data):
    
        for c in clients:
            sock.sendto(data,(c[1]))
    
            clients.append()