from Crypto.PublicKey import RSA
#from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random

""" The python documentation recomments the usage of an encryption padding, 
but this causes error messages, when encrypt and decrypt are used in a reverse
way to create and verify a signature. Therefore we use the "simple" but less
secure RSA encryption and decryption. """


# generate the key
# @return: private key object (public key can be derived by the private key)
def keygen():
	keygenerator = Random.new().read
	key = RSA.generate(1024, keygenerator)
	return key

# encrypt
# @string: message
# @key: public key
# @return: encrypted message
def encrypt(string, key):
	# use optimal asymmetric encryption padding
	# cipher = PKCS1_OAEP.new(key) 
	enc = key.encrypt(string,32)
	return enc

# decrypt
# @string: encrypted message
# @key: private key
# @return: decrypted message
def decrypt(string, key):
	# use optimal asymmetric encryption padding
	# cipher = PKCS1_OAEP.new(key)
	dec = key.decrypt(string)
	return dec

# test
if __name__ == "__main__":
	
	message = "This is the message to encrypt!!!"
	print "Message: " + message
	
	# generate the key
	key = keygen()
	print "Key: " + str(key)
	publicKey = key.publickey()
	
	# encrypt
	encMessage = encrypt(message, publicKey)
	print "Encrypted Message: " + str(encMessage)

	# decrypt
	decMessage = decrypt(encMessage, key)
	print "Decrypted Message: " + decMessage