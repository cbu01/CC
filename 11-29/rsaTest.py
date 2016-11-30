import RSAWrapper
from Crypto.PublicKey import RSA

def main():
	message = "Hello World - Iceland is great!!!"

	print "Message: " + message

	key = RSAWrapper.keygen()

	print "Key: " + str(key)

	publicKey = key.publickey()
	encMessage = RSAWrapper.encrypt(message, publicKey)

	print "Encrypted Message: " + str(encMessage)

	decMessage = RSAWrapper.decrypt(encMessage, key)

	print "Decrypted Message: " + decMessage

	return




main()
