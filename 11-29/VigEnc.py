import binascii
import os
from random import choice
from string import ascii_uppercase

salt_size = 10


def keygen():
    return os.urandom(5)


def encrypt(string, key):
    k = bin(int(binascii.hexlify(key), 16))[2:]
    string = salt_string(string)
    print "Salted string to crypt: '%s'" % string
    b = bin(int(binascii.hexlify(string), 16))[2:]


    kchain = __fitKey(len(b), k)
    enc = ''.join('0' if i == j else '1' for i, j in zip(bytearray(b), bytearray(kchain)))

    return enc


def decrypt(string, key):
    k = bin(int(binascii.hexlify(key), 16))[2:]
    kchain = __fitKey(len(string), k)

    c = ''.join('0' if i == j else '1' for i, j in zip(bytearray(string), bytearray(kchain)))
    salted_dec = binascii.unhexlify('%x' % int(c, 2))
    print "Salted decrypted string: '%s'" % salted_dec
    dec = desalt_string(salted_dec)
    return dec


def desalt_string(salted_string):
    """ Takes a decrypted salted string and removes the salt part from it """
    return salted_string[salt_size:]

def salt_string(string):
    """ Takes a string and 'salts' it by appending a random string of size salt_size """
    salt_string = ''.join(choice(ascii_uppercase) for i in range(salt_size))
    return salt_string + string

def __fitKey(messageLength, key):
    kchain = key

    while len(kchain) < messageLength:
        kchain += key
    while messageLength < len(kchain):
        kchain = kchain[:-1]
    return kchain
