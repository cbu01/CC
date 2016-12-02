import socket, pickle

def testReflectionClient():

	R_SERVER_IP = "xxxxxxx"
	R_SERVER_PORT = 10559

	HOST = ''
	CLIENT_PORT = 10000

	SERVER_ADDRESS = ("xxxxxxxx",10001) # the real server

	message = "A simple test"
	
	data = pickle.dumps((CLIENT_PORT, SERVER_ADDRESS, message))
	
	serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverSock.bind((HOST, CLIENT_PORT))
	serverSock.sendto(data, (R_SERVER_IP, R_SERVER_PORT))

	recdata, addr = serverSock.recvfrom(1024)
	reply = pickle.loads(recdata)

	print "Client receives: " + reply[2]
	print "Reflection server address: " + str(addr)

testReflectionClient()

