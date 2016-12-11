import socket
import pickle
import sys


def run(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    clients = [] # list of (id, (ip, port), publik_key(exported version))

    print "Central register service running on host {0} and port {1}".format(host, port)
    while True:

        data, addr = sock.recvfrom(2048)
        
        print "received data"
        print data
        unpickled_data = pickle.loads(data)
        print "ping"
        print "data received " + str(unpickled_data)

        if not unpickled_data in clients:
            
            print "new client"

            for c in clients:
                print "clientloop"
                # send the data to the known clients
                sock.sendto(data,(c[1]))
                print "data has been send to other clients"
                # send the client addresses to the new client
                sock.sendto(pickle.dumps(c), unpickled_data[1])
                print "new client is receiving the data for other clients"

            clients.append(unpickled_data)

if __name__ == "__main__":
    try:
        central_register_ip = sys.argv[1]
        central_register_port = int(sys.argv[2])
        run(central_register_ip, central_register_port)
    except:
        message = """Usage: python Central_Register.py central_register_ip central_register_port
         Example: python Central_Register.py localhost 10550
         """

        print message
        sys.exit()