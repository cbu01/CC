import socket, pickle
from ReflectionServerUDP.reflectionServer import *

# R_SERVER_IP = "10.2.16.168"
R_SERVER_IP = "localhost"
R_SERVER_PORT = 10559




def udp_send(ownport, ip, port, command, data):
    """ Send the given command and data to the given udp connection. """
    message = pickle.dumps((ownport, (ip, port), (command, data)))
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSock.bind(('', ownport)) # only necessary because of port forwarding
    serverSock.sendto(message, (R_SERVER_IP, R_SERVER_PORT))
    print "Send: " + str(command) + " " + str(data)


def udp_receive(ownport):
    """" Poll the udp server for message """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', ownport))

    recData, addr = s.recvfrom(1024) # 1024 is the buffersize
    data = pickle.loads(recData)

    clientPORT = data[0]
    sourceADDRESS = data[1]
    com = data[2][0]
    msg = data[2][1]
	
    print "Received: " + str(com) + " " + str(msg)
    return (com, msg)
