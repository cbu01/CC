from Crypto.Cipher import AES
from Crypto import Random
import os, binascii


class AESCipher:
    def __init__(self):
        self._key_gen()

    def _pad(self, s):
        BS = AES.block_size
        return  s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

    def _unpad(self, s):
        return s[0:-ord(s[-1])]

    def _key_gen(self):
        """ Sets hex encoded string as key """
        key = binascii.b2a_hex(os.urandom(16))  # Create a random 32 char long hex string
        self.key = key.decode("hex")

    def encrypt(self, raw):
        """ Returns hex encoded encrypted value! """
        raw = self._pad(raw)  # Pads the input with a fixed char to make its length a multiple of the block size
        iv = Random.new().read(AES.block_size);  # Our 'salt' like variable
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return (iv + cipher.encrypt(raw)).encode("hex")

    def decrypt(self, enc):
        """ Requires hex encoded param to decrypt """
        enc = enc.decode("hex")
        iv = enc[:16]
        enc = enc[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_enc = cipher.decrypt(enc)
        return self._unpad(padded_enc)


if __name__ == "__main__":
    print "AES encryption/decryption cycle: \n"
    aes_ciper = AESCipher()
    clear_text = "TEXT TO ENCRYPT"
    print "Clear text about to be encrypted: '%s'" % clear_text
    cipher_text = aes_ciper.encrypt(clear_text)
    decrypted_text = aes_ciper.decrypt(cipher_text)
    print "Decrypted text (hopefully the same as the clear text): '%s'" % decrypted_text
