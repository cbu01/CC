from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
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

def sign(string, key):
	hashValue = SHA.new(string)
	signer = PKCS_v1_5.new(key)
	signature = signer.sign(hashValue)
	return signature
	
def verify(string, key):
	hashValue = SHA.new(string)
	verifier = PKCS1_v1_5.new(key)
	if verifier.verify(h, signature):
		return True
	else:
		return False
	


