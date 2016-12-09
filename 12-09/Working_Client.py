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
                if (addr == (self.register_ip, self.register_port)):
                    client_dict_lock.aquire
                    client_dict[data[0]] = (data[1], RSA.importKey(data[2]))
                    client_dict_lock.release
                else:
                # check if received suffix is correct
        
                # if suffix is correct:
        
                # add block to blockchain
        
                # hand over parameter to calculation threads
        
        
                # restart this loop
        
        
        
    class calculationThread(threading.Thread):
        def __init__(self, threadID, name, sock):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            
            def run(self):
        
                while True:

                    # calc suffix
                    # if successful: send suffix to yourself and all other known clients
                    # check if result is ok - necessary because i don't block the prefix while it is updated
                    # this may end in a inconsistent condition
                    client_dict_lock.aquire
                    for c in client_dict:
                        sock.sendto(suffix, client_dict[c][0])
                    client_dict_lock.release
 
    def __init__(self, IP, PORT):
    
        self.IP = IP
        self.UDP_PORT = PORT

        self.sock = socket.socket(socket.AF_INT, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.UDP_PORT)) 
        
        self.client_dict = {}
        
        self.central_register_ip = "localhost"
        self.central_register_port = 10555
        
        self.key = RSAWrapper.keygen()
        self.pub_key = self.key.publicKey()
        self.ID = createHash(self.pub_key)
        
        self.client_dict[self.ID] = ((self.central_register_ip, self.central_register_port), self.pub_key)
        self.sock.sendto(self.ID, (self.central_register_ip, self.central_register_port), self.pub_key.exportKey) 
        
        client_dict_lock = threading.Lock()

        self.listen = self.listeningThread(1, "Listening_Thread", self.sock)
        self.calc_1 = self.calculationThread(2, "Calculation_Thread", self.sock)
        self.calc_2 = self.calculationThread(3, "Calculation_Thread", self.sock)
        self.calc_3 = self.calculationThread(4, "Calculation_Thread", self.sock)

        self.listen.start()
        self.calc_1.start()
        self.calc_2.start()
        self.calc_3.start()