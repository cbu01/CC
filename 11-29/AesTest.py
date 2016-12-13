from Crypto.Cipher import AES
from Crypto import Random
import os, binascii


class AESCipher:
    
    """ initialize (calls key generation) """
    def __init__(self):
        self._key_gen()

    """ add a fixed characters until len(s) is a multiple of the aes block size"""
    # @s: message string """
    # @return: padded message
    def _pad(self, s):     
        BS = AES.block_size
        return  s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

    """ remove the padding """
    # @s: padded message string 
    # @return: unpadded message string
    def _unpad(self, s):
        return s[0:-ord(s[-1])]

    """ Sets hex encoded string as key """
    def _key_gen(self):      
        key = binascii.b2a_hex(os.urandom(16))  # Create a random 32 char long hex string
        self.key = key.decode("hex")

    """ Returns hex encoded encrypted value """
    """ We add a random block in front of the message to create some salt """
    # @raw: ascii message to encrypt 
    # @return: padded and encrypted hex encoded message
    def encrypt(self, raw):
        # Pads the input with a fixed char to make its length a multiple of the block size
        raw = self._pad(raw)  
        # Our 'salt' like variable
        iv = Random.new().read(AES.block_size);  
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return (iv + cipher.encrypt(raw)).encode("hex")

    """ Decrypt message"""
    # @enc: hex encoded encrypted message 
    # @return decrypted and unpadded message in ascii 
    def decrypt(self, enc):    
        enc = enc.decode("hex")
        # get salt    
        iv = enc[:AES.block_size]
        # get message without salt  
        enc = enc[AES.block_size:] 
        # decrypt
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_enc = cipher.decrypt(enc)
        # remove padding
        return self._unpad(padded_enc)


if __name__ == "__main__":
    print "AES encryption/decryption cycle: \n"
    # init class and generate key
    aes_ciper = AESCipher()
    # encrypt message
    clear_text = "TEXT TO ENCRYPT"
    print "Clear text about to be encrypted: '%s'" % clear_text
    cipher_text = aes_ciper.encrypt(clear_text)
    # decrypt message
    decrypted_text = aes_ciper.decrypt(cipher_text)
    print "Decrypted text (hopefully the same as the clear text): '%s'" % decrypted_text
