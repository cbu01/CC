import RSAWrapper
from Crypto.PublicKey import RSA

def sign(message, key):
	signature = RSAWrapper.encrypt(message, key)
	return signature

	

def verify(message, signature, key):
	sMessage = RSAWrapper.decrypt(signature, key)
	if (message == sMessage):
		return True
	else:
		return False



