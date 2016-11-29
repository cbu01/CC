
import VigEnc

def main():
	message = "Hello World - Iceland is great!!!"

	print "Message: " + message

	key = VigEnc.keygen()

	print "Key: " + str(key)

	encMessage = VigEnc.encrypt(message, key)

	print "Encrypted Message: " + encMessage

	decMessage = VigEnc.decrypt(encMessage, key)

	print "Decrypted Message: " + decMessage

	return




main()
