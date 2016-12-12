import socket  # for sockets
import sys  # for exit
import binascii

class Bob:

	# initialize the Server of Bob
	# @portNumber: port on which the server is listening
	def __init__(self,portNumber):
		
		# initialize connection
		self.__PORT = portNumber
		self.__HOST = ''
		self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print 'Socket created'

		try:
		    self.__s.bind((self.__HOST, self.__PORT))
		except socket.error, msg:
			print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()

		print 'Socket bind complete'

		# initilize key (empty on startup)
		self.__k = ''

		return


	def Listen(self):
    	
    	# listen to incoming traffic
		self.__s.listen(10)
		print 'Socket now listening'

	    # wait to accept a connection - blocking call
		conn, addr = self.__s.accept()
		print 'Connected with ' + addr[0] + ':' + str(addr[1])

		self.__k = conn.recv(1024)
		# first message should contain the key of Alice
		print('BOB: Key received')

		# listen to further incoming messages from Alice
		while 1:
			message = conn.recv(1024)
			if not message:
				break
			# repeat key until it has the same size as the message
			kchain = self.__keyFitting(len(message))
			# decrypt
			dec = ''.join('0' if i == j else '1' for i, j in zip(bytearray(message),bytearray(kchain)))
			print 'BOB: Received message: ' + self.__turnBinToString(dec)
			conn.send('Answer from BOB: Message received')

		conn.close()
		self.__s.close()

	# turn a string from binary representation into a string of ascii characters
	# @b string in binary representation
	# @return: ascii string
	def __turnBinToString(self, b):
		s = binascii.unhexlify('%x' % int(b,2))
		return s

	# repeat key until it is as long as the message to encrypt
    # @messageLen: length of the message
    # @return: extended key
	def __keyFitting(self, messageLen):
		kchain = self.__k
		# repeat key until the key chain is equally long or longer than the message
		while len(kchain) < messageLen:
			kchain += self.__k[2:] #remove b0
        # remove the last bits of the key until its size is equal to the message length
		while messageLen < len(kchain):
			kchain = kchain[:-1]
		return kchain
	