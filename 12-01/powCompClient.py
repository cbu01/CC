import socket, binascii
import hashlib
import os
from PowHelper import *
from Crypto.Random import random

SERVER_IP = "localhost"
SERVER_PORT = 5000


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP,SERVER_PORT))

bitData = s.recv(17)

number = int(ord(bitData[-1]))
prefix = bitData[:-1]

notEnoughZeros = True
suffix = os.urandom(16)

while notEnoughZeros:
	digest = hashlib.sha256(prefix + suffix).digest()
	bin_repr = bin(int(binascii.hexlify(digest), 16))[2:].zfill(256)
	bin_suffix = bin_repr[256-number:]
	zeros = bin_suffix.count('0')
	if zeros == number:
		notEnoughZeros = False
	else:
		suffix = os.urandom(16)

s.send(suffix)

s.close()


