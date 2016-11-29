import binascii
import os

def keygen():
	return os.urandom(5)

def encrypt(string, key):
	
	b = bin(int(binascii.hexlify(string), 16))[2:]
	k = bin(int(binascii.hexlify(key), 16))[2:]

	kchain = __fitKey(len(b), k)
	enc = ''.join('0' if i == j else '1' for i, j in zip(bytearray(b),bytearray(kchain)))	

	return enc

def decrypt(string, key):
	
	k = bin(int(binascii.hexlify(key), 16))[2:]
	kchain = __fitKey(len(string), k)

	c = ''.join('0' if i == j else '1' for i, j in zip(bytearray(string),bytearray(kchain)))
	dec = binascii.unhexlify('%x' % int(c,2))
	
	return dec


def __fitKey(messageLength, key):
	kchain = key
		
	while len(kchain) < messageLength:
		kchain += key 
	while messageLength < len(kchain):
		kchain = kchain[:-1]
	return kchain
