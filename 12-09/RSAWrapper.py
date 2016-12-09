from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random
import binascii

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
	binString = __turnStringToBin(string)
	hashValue = SHA.new(binString)
	signer = PKCS1_v1_5.new(key)
	signature = signer.sign(hashValue)
	return signature
	
def verify(string, signature, key):
	binString = __turnStringToBin(string)
	hashValue = SHA.new(binString)
	verifier = PKCS1_v1_5.new(key)
	if verifier.verify(hashValue, signature):
		return True
	else:
		return False
	
def createHash(public_key):
	hasher = SHA256.new()
	hasher.update(public_key)
	return hashValue.digest()
		
	
 # turn a string into bin format without 0b         
def __turnStringToBin(string):
	b = bin(int(binascii.hexlify(string), 16))[2:]
	return b
	


