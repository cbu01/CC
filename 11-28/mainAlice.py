

from Alice import * 

def main():
	alice = Alice("192.168.1.46", 10557)
	alice.sendKeyToBob()
	alice.sendMessageToBob()
	alice.disconnect()
    
main()
