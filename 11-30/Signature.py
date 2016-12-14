import RSAWrapper
from Crypto.PublicKey import RSA

""" Caution: These functions use a modified version of the RSAWrapper (see 
comments in the RSAWrapper.py). """



""" Sign a message with a private key
@message: message that should be signed
@key: private key which is used for signing
@return: returns the signature of the message """
def sign(message, key):
	signature = RSAWrapper.decrypt(message, key)
	return signature

	
""" Verify if the message has a valid signature 
@message: message whose signature needs to be checked
@signature: signature to check
@key: public key for verification
@return: Boolean Value that indicates, if the signature is valid or not """
def verify(message, signature, key):
	sMessage = RSAWrapper.encrypt(signature, key)
	if (message == sMessage[0]):
		return True
	else:
		return False



# test
if __name__ == "__main__":
	
	message = 'A'
	print "Message: " + message

	key = RSAWrapper.keygen()
	print "Generated Key: " 
	print key

	signature = sign(str(message), key)
	print "Signature: " + str(signature)

	result = verify(message, signature, key.publickey())
	print "Result of Verification: " + str(result)
