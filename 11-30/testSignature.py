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

	# make public key private and private key public
	newPrivKey = RSA.construct((key.n, key.d, key.e))
	newPubKey = newPrivKey.publickey()

	signature = Signature.sign(str(message), key)

	print "Signature: " + str(signature)

	result = Signature.verify(message, signature, key.publickey())

	print "Result of Verification: " + str(result)

	return


main()
