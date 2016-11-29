from Crypto.Cipher import AES
from Crypto import Random
import os

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]


class AESCipher:
    def __init__(self):
        self._key_gen()

    def _key_gen(self):
        """
        Sets hex encoded param as a key
        """
        key = "140b41b22a29beb4061bda66b6747e14" #TODO not so great to have a fixed key !
        key = os.urandom(32)
        key = key[:32]
        self.key = key.decode("hex")

    def encrypt(self, raw):
        """
        Returns hex encoded encrypted value!
        """
        raw = pad(raw)
        iv = Random.new().read(AES.block_size);
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return (iv + cipher.encrypt(raw)).encode("hex")

    def decrypt(self, enc):
        """
        Requires hex encoded param to decrypt
        """
        enc = enc.decode("hex")
        iv = enc[:16]
        enc = enc[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc))


if __name__ == "__main__":
    aes_ciper = AESCipher()
    encoded_text = aes_ciper.encrypt("Some random text to encrypt. Will it work ?")
    decrypted_text = aes_ciper.decrypt(encoded_text)
    print "%s" % decrypted_text
