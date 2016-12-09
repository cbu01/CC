import threading, socket
import RSAWrapper

class Working_Client:

    class listeningThread (threading.Thread):
        def __init__(self, threadID, name, sock):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
      
        def run(self):
            while True:
        
                # listen for new messages
                data, addr = sock.recvfrom(2048)
                
                # check if it is a new client
                if (addr == (self.register_ip, self.register_port):
                    clients[data[0]] = (data[1],data)
                 
                # check if received suffix is correct
        
                # if suffix is correct: set search parameters new
        
                # add block to blockchain
        
                # hand over parameter to calculation threads
        
                # unblock
        
                # restart this loop
        
        
        
    class calculationThread(threading.Thread):
        def __init__(self, threadID, name, sock):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            
            def run(self):
        
            while True:
                # read prefix
                # calc suffix
                # if successful: send suffix to yourself and all other known clients
                # check if result is ok - necessary because i don't block the prefix while it is updated
                # this may end in a inconsistent condition
 
    def __init__(self, IP, PORT):
    
        self.IP = IP
        self.UDP_PORT = PORT

        self.sock = socket.socket(socket.AF_INT, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.UDP_PORT)) 
        
        self.client_dict = {}
        
        self.central_register_ip = "localhost"
        self.central_register_port = 10555
        
        self.key = RSAWrapper.keygen()
        self.ID = 
        
        self.sock.sendto() 

        self.listen = listeningThread(1, "Listening_Thread", self.sock)
        self.calc_1 = calculationThread(2, "Calculation_Thread", self.sock)
        self.calc_2 = calculationThread(3, "Calculation_Thread", self.sock)
        self.calc_3 = calculationThread(4, "Calculation_Thread", self.sock)

        self.listen.start()
        self.calc_1.start()
        self.calc_2.start()
        self.calc_3.start()