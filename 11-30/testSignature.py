import Signature
from Crypto.PublicKey import RSA

def main():
	message = "Hello World - Iceland is great!!!"

	print "Message: " + message

	key = RSAWrapper.keygen()

	print "Key: " + str(key)

	signature = Signature.sign(message, key)

	print "Signature: " + str(signature)

	result = Signature.verify(encMessage, key)

	print "Result of Verification: " + result

	return


main()
