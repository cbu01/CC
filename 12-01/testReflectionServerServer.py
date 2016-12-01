import socket, pickle

def testReflectionServerServer():

	SERVER = ''
	SERVER_PORT = 10559

	message = "Server Replies"
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((SERVER,SERVER_PORT))

	run = True

	while run:

		recData, addr = s.recvfrom(1024) # 1024 is the buffersize
		data = pickle.loads(recData)
		sourceADDRESSES = [data[0][0]] #assume there is just one client for the test
		msg = data[1]

		destADDRESS = addr
	
		print msg

		d = pickle.dumps((sourceADDRESSES,message))
		s.sendto(d,(destADDRESS[0],10555))

		run = False

testReflectionServerServer()



