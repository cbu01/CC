import socket, pickle
#import startupBBB


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("localhost", 10555))

#startupBBB.cleandir() # clean directory from '.pem' and '.pickle' files



clients = [] # list of (id, (ip, port), publik_key(exported version))

while True:
    
    data, addr = sock.recvfrom(2048)
    
    unpickled_data = pickle.loads(data)
        
    if not unpickled_data in clients:
    
        for c in clients:
            sock.sendto(data,(c[1]))
    
            clients.append()