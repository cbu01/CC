import socket, pickle


def reflectionServer(sourcePort, destinationPort):

	# init incoming connection

	HOST = ''

	sourceSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	sourceSocket.bind((HOST, sourcePort))

	destinationSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	destinationSocket.bind((HOST, destinationPort))

	while True:
		recData, addr = sourceSocket.recvfrom(1024) # 1024 is the buffersize
		
		data = pickle.loads(recData)

		clientPORT = data[0]
		destADDRESS = data[1]
		message = data[2]

		print "ReflectionServer receives: " + message
		print "Address: " 
		print addr

		d = pickle.dumps((clientPORT,addr,message))

		destinationSocket.sendto(d, destADDRESS)
