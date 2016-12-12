

from Alice import * 

def main():
	
	# open connection - adjust IP and Port
	alice = Alice("localhost", 10557)
	# get the key from the command line and send it to Bob
	# wait until Bob sends his key
	alice.sendKeyToBob()
	# get messages from the command line and send them to Bob
	# always waits for reply from Bob
	alice.sendMessageToBob()
	# close the connection
	alice.disconnect()
    
main()
