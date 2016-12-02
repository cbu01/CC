import socket, pickle
from PowHelper import *

SERVER_IP = "130.208.210.18"
SERVER_PORT = 5000


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP,SERVER_PORT))

bitData = s.recv(17)

print(bitData)



s.close()



# find_x_competition(prefix, level)


