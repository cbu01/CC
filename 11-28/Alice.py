import socket   #for sockets
import sys  #for exit
import binascii
 
class Alice:
    
    
	def __init__(self,remote_ip,port):
        
		try:
			#create an AF_INET, STREAM socket (TCP)
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
			sys.exit();
		print 'Socket Created'
 
		#Connect to remote server
		self.s.connect((remote_ip , port))
 
		print 'Socket Connected to ' + ' on ip ' + remote_ip

		self.k = ''
		return

	def sendKeyToBob(self):
		self.k = self.turnToBin(str(raw_input('Please enter your key:')))
		self.sendMessagesToBob(self.k)
		return

	def sendMessageToBob(self):
		m = self.turnToBin(str(raw_input('Please enter your message:')))
		kchain = self.keyFitting(len(m))
		
		enc = ''.join('0' if i == j else '1' for i, j in zip(bytearray(m),bytearray(kchain)))
		
			
		self.sendMessagesToBob(enc)
		self.receiveAnswers()
		return

	def receiveAnswers(self):
		BUFFER_SIZE = 1024
		data = self.s.recv(BUFFER_SIZE)
		print("ALICE: Message Received" + data)
		return
		
  
	def sendMessagesToBob(self, message): 
		#Send some data to remote server
		if (message=="exit"):
			return
		else:
    
 
			try :
				#Set the whole string
				self.s.send(message)
			except socket.error:
				#Send failed
				print 'Send failed'
				sys.exit()
 
			print 'Message send successfully'
		return    
    
	def disconnect(self):
		self.s.close()
		return

	def turnToBin(self, string):
		b = bin(int(binascii.hexlify(string), 16))[2:]
		return b
	
	def keyFitting(self, messageLen):
		kchain = self.k
		
		while len(kchain) < messageLen:
			kchain += self.k[2:] #remove b0
		while messageLen < len(kchain):
			kchain = kchain[:-1]
		return kchain
    
