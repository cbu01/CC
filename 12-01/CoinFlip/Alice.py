import socket, pickle
from Crypto.Random import random
from Crypto.Hash import SHA256

""" Alice connects to Bob (he has to be started BEFORE Alice). She flips a coin
and generates the hash value of the coin and a random suffix. She sends this 
has value to Bob. Bob flips his coin and sends his hash value then to Alice.
Alice sends the value of the coin and the suffix to Bob, so he can check, if she
told him the truth. Bob then sends Alice his suffix and coin value and she 
checks, if he told the truth. 
This implementation uses the reflection server!!! """
def AliceCoinFlip():
	
	host_A = "localhost"
	port_A = 10000
	host_B = "localhost"
	port_B = 10001
	rServer_ip = "localhost"
	rServer_port = 10555

	buffer_size = 1024 #bytes

	# initialize socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #dont block when program crashes
	s.bind((host_A, port_A))

	# generate coinflip and cipher
	b_A = random.getrandbits(1)
	c, suffix = commit(b_A)
	print "Coin of Alice: " + str(b_A)

	# send data to Bob

	data = pickle.dumps((port_A, (host_B, port_B), c))
	s.sendto(data, (rServer_ip, rServer_port))

	# receive cipher from Bob
	recdata, addr = s.recvfrom(1024)
	coin_b = pickle.loads(recdata)
	c_B = coin_b[2]

	# send coinflip and nonce to Bob 
	data = pickle.dumps((port_A, (host_B, port_B), (b_A, suffix)))
	s.sendto(data, (rServer_ip, rServer_port))

	# receive coinflip and nonce from Bob
	recdata, addr = s.recvfrom(1024)
	coin_b = pickle.loads(recdata)
	b_B, suffix_B = coin_b[2]

	# reveal
	if (reveal(b_B, c_B, suffix_B)):
		print "Bob tells the truth"
		result = (b_B^b_A)
		print "Result of the coinflip: " + str(result)
	else:
		print "Bob does not tell the truth"


""" add a random suffix to the value of the coin and generate its hash
value
@b_A: a random bit - can be 0 or 1 
@return: hash value and random suffix"""	
def commit(b_A):
	
	Min = 255 # bits
	Max = 2048 # bits

	suffix_length = random.randint(Min, Max)
	suffix = random.getrandbits(suffix_length)

	h = SHA256.new()
	h.update(str(b_A))
	h.update(str(suffix)) # appends suffix
	c = h.digest()

	return c, suffix

""" Check if the hash value of the claimed result of the coinflip and the 
given suffix corresponds to the hash value received before.
@b_B: value of the coin (0 or 1)
@c_B: hash value from coin and suffix
@suffix_B: suffix 
@return: Boolean value"""
def reveal(b_B, c_B, suffix_B):

	h = SHA256.new()
	h.update(str(b_B))
	h.update(str(suffix_B)) # appends suffix
	real_C = h.digest()

	if (c_B == real_C):
		return True
	else:
		return False

""" Start Alice """
if __name__ == "__main__":
	AliceCoinFlip()	
	
