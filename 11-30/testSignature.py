import Signature
import RSAWrapper
import sys
from Crypto.PublicKey import RSA

def main():

	message = 'A'

	print "Message: " + message

	key = RSAWrapper.keygen()

	print "Key: " 
	print key

	signature = Signature.sign(str(message), key)

	print "Signature: " + str(signature)

	result = Signature.verify(message, signature, key.publickey())

	print "Result of Verification: " + str(result)

	return


main()
