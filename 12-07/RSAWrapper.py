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
	newString = ""
	while (len(string) >= 54):
		stringToEncrypt = string[0:54]
		cipher = PKCS1_OAEP.new(key)
		enc = cipher.encrypt(stringToEncrypt)
		newString = newString + enc
		string = string[54:]
	stringToEncrypt = string
	cipher = PKCS1_OAEP.new(key)
	enc = cipher.encrypt(stringToEncrypt)
	newString = newString + enc
	return newString

def decrypt(string, key):
	newString = ""
	while (len(string) > 0):
		stringToDecrypt = string[0:128]
		cipher = PKCS1_OAEP.new(key)
		dec = cipher.decrypt(stringToDecrypt)
		newString = newString + dec
		string = string[128:]
	return newString

def sign(string, key):
	hashValue = SHA.new(string)
	signer = PKCS1_v1_5.new(key)
	signature = signer.sign(hashValue)
	return signature
	
def verify(string, signature, key):
	hashValue = SHA.new(string)
	verifier = PKCS1_v1_5.new(key)
	if verifier.verify(hashValue, signature):
		return True
	else:
		return False
	


