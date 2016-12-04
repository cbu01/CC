import socket, pickle
from Crypto.Random import random
from Crypto.Hash import SHA256

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


def reveal(b_B, c_B, suffix_B):

	h = SHA256.new()
	h.update(str(b_B))
	h.update(str(suffix_B)) # appends suffix
	real_C = h.digest()

	if (c_B == real_C):
		return True
	else:
		return False

AliceCoinFlip()	
	
