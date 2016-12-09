import threading, socket
import RSAWrapper
import ProofOfWork
from BlockChain import BlockChain
from Block import Block
import time
import pickle
import RSA
import Common


class Working_Client:

    class listeningThread (threading.Thread):
        def __init__(self, threadID, name, sock, block_chain):
            threading.Thread.__init__(self)
            self.block_chain = block_chain
            self.sock = sock
            self.threadID = threadID
            self.name = name
      
        def run(self):
            while True:
        
                # listen for new messages
                data, addr = self.sock.recvfrom(2048)

                # check if it is a new client
                if (addr == (self.register_ip, self.register_port)):
                    self.client_dict_lock.aquire
                    self.client_dict[data[0]] = (data[1], RSA.importKey(data[2]))
                    self.client_dict_lock.release
                else:
                    deserialized_block = pickle.loads(data[0], 'rb')
                    new_block_verified = ProofOfWork.verify_next_block_in_chain(deserialized_block, self.block_chain)
                    if new_block_verified:
                        self.block_chain.add_block(deserialized_block)

                    # TODO somehow update the blocks of all calculations threads
        
        
    class calculationThread(threading.Thread):
        def __init__(self, threadID, name, sock, block_without_nonce, client_name):
            threading.Thread.__init__(self)
            self.client_name = client_name
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
                                print "Thread {0} from client {1} found a nonce and thinks its the first one !".format(self.threadID,
                                                                                                         self.client_name, )
                                # Broadcast the block
                                self.client_dict_lock.aquire
                                serialized_block = pickle.dumps(self.block, 'wb')
                                for c in self.client_dict:
                                    sock.sendto(serialized_block, self.client_dict[c][0])
                                self.client_dict_lock.release
                                self.update_block()
                                continue
                            else:
                                # Found a block but someone was faster :(
                                print "Thread {0} from client {1} found a nonce but was too slow".format(self.threadID, self.client_name)
                                self.update_block()
                                continue
                    self.update_block()

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
        self.ID = Common.client_id_from_public_key(self.pub_key)
        
        self.client_dict[self.ID] = ((self.central_register_ip, self.central_register_port), self.pub_key)
        self.sock.sendto(self.ID, (self.central_register_ip, self.central_register_port), self.pub_key.exportKey) 
        
        self.client_dict_lock = threading.Lock()
        
        # initialize genesis here!!!!

        block_chain = BlockChain()
        block_without_nonce1 = Working_Client.create_next_block(block_chain, client_name)
        block_without_nonce2 = Working_Client.create_next_block(block_chain, client_name)
        block_without_nonce3 = Working_Client.create_next_block(block_chain, client_name)

        self.listen = self.listeningThread(1, "Listening_Thread", self.sock, block_chain)
        self.calc_1 = self.calculationThread(2, "Calculation_Thread", self.sock, block_without_nonce1)
        self.calc_2 = self.calculationThread(3, "Calculation_Thread", self.sock, block_without_nonce2)
        self.calc_3 = self.calculationThread(4, "Calculation_Thread", self.sock, block_without_nonce3)

        self.listen.start()
        self.calc_1.start()
        self.calc_2.start()
        self.calc_3.start()

    @staticmethod
    def create_next_block(block_chain, client_name):
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