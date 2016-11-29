import socket  # for sockets
import sys  # for exit
import binascii

class Bob:

	def __init__(self,portNumber):
		self.PORT = portNumber
		self.HOST = ''

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print 'Socket created'

		try:
		    self.s.bind((self.HOST, self.PORT))
		except socket.error, msg:
			print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()

		print 'Socket bind complete'

		self.k = ''

		return


	def Listen(self):
    	
		self.s.listen(10)
		print 'Socket now listening'

	    # wait to accept a connection - blocking call
		conn, addr = self.s.accept()
		print 'Connected with ' + addr[0] + ':' + str(addr[1])

		self.k = conn.recv(1024)
		print('BOB: Key received')

		while 1:
			message = conn.recv(1024)
			if not message:
				break
			kchain = self.keyFitting(len(message))
			dec = ''.join('0' if i == j else '1' for i, j in zip(bytearray(message),bytearray(kchain)))
			print 'BOB: Received message: ' + self.turnBinToString(dec)
			conn.send('BOB: Message received')

		conn.close()
		self.s.close()

	def turnBinToString(self, b):
		s = binascii.unhexlify('%x' % int(b,2))
		return s

	def keyFitting(self, messageLen):
		kchain = self.k
		
		while len(kchain) < messageLen:
			kchain += self.k[2:] #remove b0
		while messageLen < len(kchain):
			kchain = kchain[:-1]
		return kchain

