from Crypto.PublicKey import RSA
from Crypto import Random

def keygen():
	keygenerator = Random.new().read
	key = RSA.generate(1024, keygenerator)
	return key

def encrypt(string, key):
	publicKey = key.publickey()
	enc = publicKey.encrypt(string,32)
	return enc

def decrypt(string, key):
	dec = key.decrypt(string)
	return dec 


