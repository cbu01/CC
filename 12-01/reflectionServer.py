import socket, pickle


def reflectionServer(sourcePort, destinationPort):

	# init incoming connection

	HOST = ''

	sourceSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	sourceSocket.bind((HOST, sourcePort))

	destinationSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	while True:
		recData, addr = sourceSocket.recvfrom(1024) # 1024 is the buffersize
		
		data = pickle.loads(recData)

		destADDRESSES = data[0]
		message = data[1]

		sourceADDRESS = [addr]

		d = pickle.dumps((sourceADDRESS,message))

		for i in xrange(len(destADDRESSES)):
			destinationSocket.sendto(d, destADDRESSES[i])
