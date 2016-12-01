import RSAWrapper
from Crypto.PublicKey import RSA

def sign(message, key):
	#signature = RSAWrapper.encrypt(message, key)
	signature = RSAWrapper.decrypt(message, key)
	return signature

	

def verify(message, signature, key):
	#sMessage = RSAWrapper.decrypt(signature, key)
	sMessage = RSAWrapper.encrypt(signature, key)
	if (message == sMessage[0]):
		return True
	else:
		return False



