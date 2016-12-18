import socket, pickle
from Crypto.Random import random
from Crypto.Hash import SHA256


""" Start Bob before you start Alice!!! """

""" Bob waits for connection from Alice and in order to receive the hash value
of her coin. Then Bob throws his coin and sends the hash value of the coin and 
random suffix to Alice. Alice reveals the value of her coin and Bob reveals 
his. Bob checks, if Alice told him the truth. The final result is the XOR 
value of both coints.
This implementation uses the reflection server!!! """
def BobCoinFlip():
	
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
	s.bind((host_B, port_B))

	# receive cipher from Alice
	recdata, addr = s.recvfrom(1024)
	coin_a = pickle.loads(recdata)
	c_A = coin_a[2]

	# generate coinflip and cipher
	b_B = random.getrandbits(1)
	c, suffix = commit(b_B)
	print "Coin of Bob: " + str(b_B)

	# send data to Alice
	data = pickle.dumps((port_B, (host_A, port_A), c))
	s.sendto(data, (rServer_ip, rServer_port))

	# receive coinflip and nonce from Alice
	recdata, addr = s.recvfrom(1024)
	coin_a = pickle.loads(recdata)
	b_A, suffix_A = coin_a[2]

	

	# send coinflip and nonce to Alice
	data = pickle.dumps((port_B, (host_A, port_A), (b_B, suffix)))
	s.sendto(data, (rServer_ip, rServer_port))

	# reveal
	if (reveal(b_A, c_A, suffix_A)):
		print "Alice tells the truth"
		result = (b_B^b_A)
		print "Result of the coinflip: " + str(result)
	else:
		print "Alice does not tell the truth"


""" add a random suffix to the value of the coin and generate its hash
value
@b_B: a random bit - can be 0 or 1 
@return: hash value and random suffix"""	
def commit(b_B):
	
	Min = 255 # bits
	Max = 2048 # bits

	suffix_length = random.randint(Min, Max)
	suffix = random.getrandbits(suffix_length)

	print "suffix length " + str(suffix_length)

	h = SHA256.new()
	h.update(str(b_B))
	h.update(str(suffix)) # appends suffix
	c = h.digest()

	return c, suffix

""" Check if the hash value of the claimed result of the coinflip and the 
given suffix corresponds to the hash value received before.
@b_A: value of the coin (0 or 1)
@c_A: hash value from coin and suffix
@suffix_A: suffix 
@return: Boolean value"""
def reveal(b_A, c_A, suffix_A):

	h = SHA256.new()
	h.update(str(b_A))
	h.update(str(suffix_A)) # appends suffix
	real_C = h.digest()

	if (c_A == real_C):
		return True
	else:
		return False

""" Start Bob """
if __name__ == "__main__":
	BobCoinFlip()
	
