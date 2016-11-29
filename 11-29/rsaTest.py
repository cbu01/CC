import RSAWrapper

def main():
	message = "Hello World - Iceland is great!!!"

	print "Message: " + message

	key = RSAWrapper.keygen()

	print "Key: " + str(key)

	encMessage = RSAWrapper.encrypt(message, key)

	print "Encrypted Message: " + str(encMessage)

	decMessage = RSAWrapper.decrypt(encMessage, key)

	print "Decrypted Message: " + decMessage

	return




main()
