import socket, pickle

def testReflectionClient():

	R_SERVER_IP = "10.2.16.168"
	R_SERVER_PORT = 10555
	receiver_addresses = [("10.2.16.168",10559)] # the real servers

	message = "A simple test"
	
	data = pickle.dumps((receiver_addresses, message))
	
	serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverSock.sendto(data, (R_SERVER_IP, R_SERVER_PORT))

	recdata, addr = serverSock.recvfrom(1024)
	reply = pickle.loads(recdata)

	print reply[1]

testReflectionClient()

