import pickle, socket

class Client:

	def __init__(self, ID):
		self.ID = ID
		self.BBBhost = "localhost"
		self.BBBport = 10555
		#init socket
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#######################################################################

	def __sendMessage(self, message):
		self.s.sendto(message, (self.BBBhost, self.BBBport))
		return

	def __receiveMessage(self):
		message, addr = self.s.receivefrom(1024)
		return message

	#######################################################################

	def __pay(self, id2, amount):
		try:
			a = float(amount) #cast amount to float
			if (a <= 0):
				print "transaction not successful - choose a positive amount of money"
			else:
				message = pickle.dumps("PAY", self.ID, id2, a)
				self.__sendMessage(message)
				reply = self.__receiveMessage()
				if type(reply) == bool:
					if (reply == False):
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
			message = pickle.dumps("QUERY", self.ID, id2, transactionID, amount)
			self.__sendMessage(message)
			reply = self.__receiveMessage()
			if reply:
				print "Money received"
				return
			else:
				print "Money has not been received"
				return
		except ValueError:
			print "transaction not successful - enter amount as a number"
			return
			
		

	#######################################################################

	def mainLoop(self):
		loop = True
		while loop:
			x = raw_input(">: ").split()
			if (x[0] == "pay"):
				self.__pay(x[1],x[2])
			elif (x[1] == "query"):
				self.__query(x[1],x[2],x[3])
			elif (x[0] == "quit"):
				loop = False
			else:
				print "Please enter something useful"



