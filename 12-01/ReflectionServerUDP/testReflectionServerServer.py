import socket, pickle

def testReflectionServerServer():

	SERVER = ''
	SERVER_PORT = 10001

	message = "Server Replies"
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((SERVER,SERVER_PORT))

	run = True

	while run:

		recData, addr = s.recvfrom(1024) # 1024 is the buffersize
		data = pickle.loads(recData)
		clientPORT = data[0]
		sourceADDRESS = data[1]
		msg = data[2]
	
		print "Server receives: " + msg

		d = pickle.dumps((SERVER_PORT, (sourceADDRESS[0],clientPORT),message))
		s.sendto(d,(addr[0],10559))

		run = False

testReflectionServerServer()



