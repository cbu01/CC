import threading, socket
import RSAWrapper
import ProofOfWork
from BlockChain import BlockChain
from Block import Block
import time

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
                    self.client_dict_lock.aquire
                    self.client_dict[data[0]] = (data[1], RSA.importKey(data[2]))
                    self.client_dict_lock.release
                else:
                    # check if received suffix is correct
        
                    # if suffix is correct:
        
                        # add block to blockchain
        
                    # update prefix
            
        
        
    class calculationThread(threading.Thread):
        def __init__(self, threadID, name, sock, block_without_nonce):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.block = block_without_nonce
            self.next_block_found_by_someone = False
            
            def run(self):
                while True:
                    for i in range(1000):
                        found_nonce = ProofOfWork.try_to_set_correct_nonce(self.block)
                        if found_nonce:
                            # Check if somebody else already found the next block
                            if not self.next_block_found_by_someone:
                                # Broadcast the block
                                self.client_dict_lock.aquire
                                for c in self.client_dict:
                                    # TODO should pickle the block before sending it. Unpickle it on the other side
                                    sock.sendto(self.block, self.client_dict[c][0])
                                self.client_dict_lock.release
                                self.update_block()
                                continue
                            else:
                                # Found a block but someone was faster :(
                                self.update_block()
                                continue
                    self.update_block()

                    # calc suffix
                    # if successful: send suffix to yourself and all other known clients
                    
                        # check if result is ok - necessary because i don't block the prefix while it is updated
                        # this may end in a inconsistent condition

            def update_block(self):
                # TODO
                pass

    def __init__(self, IP, PORT, client_name):
    
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
        
        self.client_dict_lock = threading.Lock()

        block_chain = BlockChain()
        block_without_nonce = self.create_first_block_without_nonce(block_chain, client_name)

        self.listen = self.listeningThread(1, "Listening_Thread", self.sock, block_without_nonce)
        self.calc_1 = self.calculationThread(2, "Calculation_Thread", self.sock, block_without_nonce)
        self.calc_2 = self.calculationThread(3, "Calculation_Thread", self.sock, block_without_nonce)
        self.calc_3 = self.calculationThread(4, "Calculation_Thread", self.sock, block_without_nonce)

        self.listen.start()
        self.calc_1.start()
        self.calc_2.start()
        self.calc_3.start()


    def create_first_block_without_nonce(self, block_chain, client_name):
        prev_block = block_chain.get_latest_block()
        timestamp = int(time.time())
        data = client_name
        new_counter = prev_block.get_counter() + 1
        hash_difficulty_value = 15

        block = Block(prev_block,
                      prev_block.get_hash_value(),
                      timestamp,
                      data,
                      new_counter,
                      hash_difficulty_value)

        return block