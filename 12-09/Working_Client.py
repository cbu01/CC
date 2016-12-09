import threading, socket
import RSAWrapper
import ProofOfWork
from BlockChain import BlockChain
from Block import Block
import time
import pickle
from Crypto.PublicKey import RSA
import Common




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

def startClient(IP, PORT, client_name):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT)) 
        
    client_dict = {}
       
    central_register_ip = "localhost"
    central_register_port = 10555
      
    key = RSAWrapper.keygen()
    pub_key = key.publicKey()
    ID = Common.client_id_from_public_key(pub_key)
     
    client_dict[ID] = ((central_register_ip, central_register_port), pub_key)
    sock.sendto(ID, (central_register_ip, central_register_port), pub_key.exportKey) 
      
    client_dict_lock = threading.Lock()

    block_chain = BlockChain()
    block_without_nonce1 = create_next_block(block_chain, client_name)
    block_without_nonce2 = create_next_block(block_chain, client_name)
    block_without_nonce3 = create_next_block(block_chain, client_name)
    listen = listeningThread(1, "Listening_Thread", sock, block_chain)
    calc_1 = calculationThread(2, "Calculation_Thread", sock, block_without_nonce1)
    calc_2 = calculationThread(3, "Calculation_Thread", sock, block_without_nonce2)
    calc_3 = calculationThread(4, "Calculation_Thread", sock, block_without_nonce3)
    listen.start()
    calc_1.start()
    calc_2.start()
    calc_3.start()


def create_next_block(block_chain, client_name):
    prev_block = block_chain.get_latest_block()
    timestamp = int(time.time())
    data = client_name
    new_counter = prev_block.get_counter() + 1
    hash_difficulty_value = 15
    block = Block(prev_block, prev_block.get_hash_value(), timestamp, data, new_counter, hash_difficulty_value)

    return block

startClient("localhost",15000, "I AM YOUR FATHER")