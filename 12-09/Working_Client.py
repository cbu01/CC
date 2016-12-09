import threading, socket
import RSAWrapper
import ProofOfWork
from BlockChain import BlockChain
from Block import Block
import time
import pickle
from Crypto.PublicKey import RSA
import Common
import Queue


class listeningThread (threading.Thread):
    def __init__(self, threadID, name, sock, block_chain, block_update_queues):
        threading.Thread.__init__(self)
        self.block_update_queues = block_update_queues
        self.block_chain = block_chain
        self.sock = sock
        self.threadID = threadID
        self.name = name
      
    def run(self):
        print "listeningThread is active"
        while True:
    
            # listen for new messages
            data, addr = self.sock.recvfrom(4096)
            # check if it is a new client
            if addr == (central_register_ip, central_register_port):
                client_dict_lock.acquire()
                client_dict[data[0]] = (data[1], RSA.importKey(data[2]))
                client_dict_lock.release()
            else:
                deserialized_block = pickle.loads(data)
                new_block_verified = ProofOfWork.verify_next_block_in_chain(deserialized_block, self.block_chain)
                if new_block_verified:
                    self.block_chain.add_block(deserialized_block)
                    print "Block number {0} was added to the block chain".format(str(deserialized_block.get_counter()))
                    for queue in self.block_update_queues:
                        next_block = create_next_block(self.block_chain, "will_be_updated_by_client")
                        queue.put(next_block)
                else:
                    print "Got a proposed new block but it did not verify"
        

class calculationThread(threading.Thread):
    def __init__(self, threadID, name, sock, block_without_nonce, client_name, block_update_queue):
        threading.Thread.__init__(self)
        self.block_update_queue = block_update_queue
        self.client_name = client_name
        self.threadID = threadID
        self.name = name
        self.block = block_without_nonce

    def run(self):
        print "calculationThread is active"
        while True:
            for i in range(1000):
                found_nonce = ProofOfWork.try_to_set_correct_nonce(self.block)
                if found_nonce:
                    # Check if somebody else already found the next block
                    someone_already_found_block = not self.block_update_queue.empty()
                    if not someone_already_found_block:
                        print "Thread {0} from client {1} found a nonce and thinks its the first one !".format(self.threadID,
                                                                                                 self.client_name, )
                        # Broadcast the block
                        client_dict_lock.acquire()
                        serialized_block = pickle.dumps(self.block)
                        for c in client_dict:
                            sock.sendto(serialized_block, client_dict[c][0])
                        client_dict_lock.release()
                        self.update_block()
                        continue
                    else:
                        # Found a block but someone was faster :(
                        print "Thread {0} from client {1} found a nonce but was too slow".format(self.threadID, self.client_name)
                        self.update_block()
                        continue
            self.update_block()

    def update_block(self):
        if not self.block_update_queue.empty():
            self.block = self.block_update_queue.get()
            self.block.data = self.client_name


def create_next_block(block_chain, client_name):
    prev_block = block_chain.get_latest_block()
    timestamp = int(time.time())
    data = client_name
    new_counter = prev_block.get_counter() + 1
    hash_difficulty_value = 15
    block = Block(prev_block, prev_block.get_hash_value(), timestamp, data, new_counter, hash_difficulty_value)

    return block


HOST = "localhost"
PORT = 15000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT)) 
        
client_dict = {}
       
central_register_ip = "localhost"
central_register_port = 10555
      
key = RSAWrapper.keygen()
pub_key = key.publickey()
ID = Common.client_id_from_public_key(pub_key)
     
client_dict[ID] = ((HOST, PORT), pub_key)
serialized_message = pickle.dumps((ID, (HOST,PORT),pub_key))
sock.sendto(serialized_message, (central_register_ip, central_register_port))
      
client_dict_lock = threading.Lock()

client_name = "random_client_name"
block_chain = BlockChain()
block_without_nonce1 = create_next_block(block_chain, client_name)
block_without_nonce2 = create_next_block(block_chain, client_name)
block_without_nonce3 = create_next_block(block_chain, client_name)

queue1 = Queue.Queue()
queue2 = Queue.Queue()
queue3 = Queue.Queue()

listen = listeningThread(1, "Listening_Thread", sock, block_chain, [queue1, queue2, queue3])
calc_1 = calculationThread(2, "Calculation_Thread", sock, block_without_nonce1, client_name, queue1)
calc_2 = calculationThread(3, "Calculation_Thread", sock, block_without_nonce2, client_name, queue2)
calc_3 = calculationThread(4, "Calculation_Thread", sock, block_without_nonce3, client_name, queue3)
listen.start()
calc_1.start()
calc_2.start()
calc_3.start()