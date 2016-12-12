from Bob import *

def main():
	
	# start Bobs Server on specified port
	bob = Bob(10557)
	# listen to the incoming traffic
	bob.Listen()

main()
