from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random

def keygen():
	keygenerator = Random.new().read
	key = RSA.generate(1024, keygenerator)
	return key

def encrypt(string, key):
	cipher = PKCS1_OAEP.new(key)
	enc = cipher.encrypt(string)
	return enc

def decrypt(string, key):
	ciper = PKCS1_OAEP.new(key)
	dec = ciper.decrypt(string)
	return dec


