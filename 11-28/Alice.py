import socket   #for sockets
import sys  #for exit
import binascii
 
 
 
 
class Alice: 
    
    # init class object and initialize the tcp connection
    # @remote_ip: IP of Bob
    # @port: Port of Bob
    def __init__(self, remote_ip, port):
        
		try:
			#create an AF_INET, STREAM socket (TCP)
			self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
			sys.exit();
		print 'Socket Created'
 
		#Connect to remote server
		self.__s.connect((remote_ip , port))
 
		print 'Socket Connected to ' + ' on ip ' + remote_ip
        
        # init empty key
		self.__k = ''
		return

    # get the key from the standard input and send it to Bob
    def sendKeyToBob(self):
		self.__k = self.__turnToBin(str(raw_input('Please enter your key:')))
		self.__sendMessagesToBob(self.__k)
		return

    # encrypt the message and call function to send the message, waits for answer
    def sendMessageToBob(self):
        
        # get message an turn it into binary representation
		m = self.__turnToBin(str(raw_input('Please enter your message:')))
        
        # repeat the key until it is equally long to the message
		kchain = self.__keyFitting(len(m))
		
        # encryption: perform XOR 
		enc = ''.join('0' if i == j else '1' for i, j in zip(bytearray(m),bytearray(kchain)))
			
        # send message and wait for answer
		self.__sendMessagesToBob(enc)
		self.__receiveAnswers()
		return

    # receive answers from Alice
    def __receiveAnswers(self):
        BUFFER_SIZE = 1024
        data = self.__s.recv(BUFFER_SIZE)
        print("ALICE: Message Received from Bob: " + data)
        return
	
    # close connection on message "exit"; send the message to Bob otherwise
    # @message: encrypted message
    def __sendMessagesToBob(self, message):
         
        #Send some data to remote server
        if (message=="exit"):
            disconnect(self)
        else:
            try :
                #Set the whole string
                self.__s.send(message)
            except socket.error:
                #Send failed
                print 'Send failed'
                sys.exit()
 
            print 'Message send successfully'
        return    
    
    # close the connection
    def disconnect(self):
        self.__s.close()
        return

    # convert a string into its binary representation
    # @string: ascii string to convert
    # @return: binary representation of the string 
    def __turnToBin(self, string):
		b = bin(int(binascii.hexlify(string), 16))[2:]
		return b
	
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
    
