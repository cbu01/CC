import binascii
import os
from random import choice
from string import ascii_uppercase
from Crypto.Random import random

salt_size = 10

""" Assumptions: 
    - Only letters are used, no numbers, no special characters
    - Only uppercase letters are used (lowercase letters are converted), this
      also adds some salt to the message (eg. names usually start with an upper
      letter...)
    - Salt: whitespaces are eliminated (cannot be restored but humens should
      still be able to understand the message
    - Salt: Some string with random characters is appended to the message """




""" Generates key of given length 
    @length: desired key length
    @return: key consisting of uppercase letters """
def keygen(length):
    newKey = ""
    for x in range(length):
        # choose random letter between 'A' and 'Z'
        r = random.randint(65,90)
        newKey += (chr(r))
    return newKey

""" Salts and encrypts a message
    @string: message to encrypt
    @key: key to use for the encryption
    @return: salted and encrypted message """
def encrypt(string, key):
    
    # prepare string (converst all letters to uppercase letters and remove whitespaces
    string = string.upper()
    string = ''.join(string.split())
    
    # salt string
    string = salt_string(string)
    print "Salted string to crypt: '%s'" % string
    
    # increase keysize to message length - ignore whitespaces
    # the key might be too long for the message, if special characters or numbers
    # are used, but that does not cause any problems, since these characters 
    # simply remain unused
    keychain = __prepareKey(len(string), key)
      
    # encrypt string
    enc_string = "" 
    for s in string:
        # character is between 'A' and 'Z' -> encrypt
        if (ord(s) >= 65 and ord(s) <= 90):
            enc_string += chr(((ord(s) - 65 + int(keychain[0])) % 26) + 65)
            keychain = keychain[1:]
        # otherwise: just leave the character as it is
        else:
            enc_string += s
            
    return enc_string


""" decrypt a message
    @string: message to decrypt 
    @key: key to use for decryption
    @return: decrypted and unsalted message """
def decrypt(string, key):
    
    # increase keysize to message length - ignore whitespaces
    keychain = __prepareKey(len(string), key)
    
    dec_string = ""
    for s in string:
        # character is between 'A' and 'Z' -> decrypt
        if (ord(s) >= 65 and ord(s) <= 90):
            dec_string += (chr(((ord(s) - 65 - int(keychain[0])) % 26) + 65))
            keychain = keychain[1:]
        # otherwise just take the character as it is
        else:
            dec_string += s
            
    print "Salted decrypted string: '%s'" % dec_string
    dec = desalt_string(dec_string)
    
    return dec

""" removes random salt-string from a decrypted message
    @salted_string: salted string
    @return: unsalted string """
def desalt_string(salted_string):
    return salted_string[salt_size:]

""" adds a random string with a predefined length to the beginning of the not 
    yet encrypted message
    @string: unsalted string
    @return: salted string """
def salt_string(string):
    salt_string = ''.join(choice(ascii_uppercase) for i in range(salt_size))
    return salt_string + string

""" extracts the number of positions to shift the letters from the key and 
    increases the key length to message length
    @key: key to increase
    @return: key which is used for encryption or decryption """
def __prepareKey(messageLength, key):
    # calculate shift from each letter
    key_in_numbers = ""
    for k in key:
        shift = (ord(k) - 65) 
        key_in_numbers += str(shift) 
        
    # repeat key according to message length
    kchain = key_in_numbers
    # repeat key until it is at least as long as the message
    while len(kchain) < messageLength:
        kchain += key_in_numbers
    # remove superfluous characters
    while messageLength < len(kchain):
        kchain = kchain[:-1]
    return kchain


""" Test if everything works """
if __name__ == "__main__":
    
    # generate message
    message = "Hello World!!! Try to read this message!!!"
    print "Message: " + message

    # generate key
    key = keygen(5)
    print "Key: " + str(key)

    # encrypt message
    encMessage = encrypt(message, key)
    print "Encrypted Message: " + encMessage

    # decrypt message
    decMessage = decrypt(encMessage, key)
    print "Decrypted Message: " + decMessage
    
    
    