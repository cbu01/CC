from RSAWrapper import *
from Crypto.PublicKey import RSA

def sign(message, key):
	signature = RSAWrapper.encrypt(message, key)
	return signature

	

def verify(message, signature, key):
	vKey = __turnAroundKey(key)
	sMessage = RSAWrapper.decrypt(message, key)
	if (message == sMessage):
		return true
	else:
		return false



