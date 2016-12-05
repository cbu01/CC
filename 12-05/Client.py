import pickle, socket, os, sys
import Common
import RSAWrapper

class Client:

	def __init__(self, ID):
		self.ID = ID
		self.BBBhost = "localhost"
		self.BBBport = 10555
		
		self._BBB_key = pickle.load(open("BBBPublicKey.pickle", "rb"))
		
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		self._key = self._load_keys(str(ID)+"PrivateKey.pickle")
		
		

	#######################################################################

	def __sendMessage(self, message):
		self.s.sendto(message, (self.BBBhost, self.BBBport))
		return

	def __receiveMessage(self):
		message, addr = self.s.recvfrom(2048)
		return message

	#######################################################################

	def __pay(self, id2, amount):
		try:
			a = float(amount) #cast amount to float
			if (a <= 0):
				print "transaction not successful - choose a positive amount of money"
			else:
				message = pickle.dumps(("PAY", self.ID, Common.int_to_id(id2), a))
				self.__sendMessage(message)
				reply = self.__receiveMessage()
				if (reply == "False"):
					print "transaction not successfull - rejected by BBB"
					return
				else:
					print "transaction successful with transaction ID: " + str(reply)
					return				 
		except ValueError:
			print "transaction not successful - enter amount as a number"
			return

	def __query(self, id2, transactionID, amount):
		try:
			a = float(amount) #cast amount to float
			message = pickle.dumps(("QUERY", Common.int_to_id(id2) , self.ID, Common.int_to_id(transactionID), amount))
			self.__sendMessage(message)
			reply = self.__receiveMessage()
			if (reply == "True"):
				print "Money received"
				return
			else:
				print "Money has not been received"
				return
		except ValueError:
			print "transaction not successful - enter amount as a number"
			return
		
		
	######################################################################
	
	def _data_file_exists(self, data_file_name):
		cwd = os.getcwd()
		file_path = os.path.join(cwd, data_file_name)
		return os.path.isfile(file_path)
       
	def _load_keys(self, key_file_name):
		key_file_exists = self._data_file_exists(key_file_name)
		if not key_file_exists:
			_key = RSAWrapper.keygen()
			pickle.dump(_key, open(key_file_name, "wb"))
			self._register(_key.publickey())
		else:
			_key = pickle.load(open(key_file_name, "rb"))

		return _key
       
	def _register(self, _public_key):
		r_message = pickle.dumps(("REGISTER", self.ID, _public_key))
		self.__sendMessage(r_message)
		reply = self.__receiveMessage()
		if (reply == "True"):
			print "Successfully registered"
			return
		else :
			print "Registration not possible"
			sys.exit(0)
			return
					

	#######################################################################

	def mainLoop(self):
		loop = True
		while loop:
			x = raw_input(">: ").split()
			print x
			if (x[0] == "pay"):
				self.__pay(x[1],x[2])
			elif (x[0] == "query"):
				self.__query(x[1],x[2],x[3])
			elif (x[0] == "quit"):
				loop = False
			else:
				print "Please enter something useful"



