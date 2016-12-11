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
import sys


class listeningThread(threading.Thread):
    def __init__(self,
                 threadID,
                 name,
                 sock,
                 block_chain,
                 client_name,
                 block_update_queues,
                 central_register_ip,
                 central_register_port,
                 client_dict):
        threading.Thread.__init__(self)
        self.client_dict = client_dict
        self.central_register_port = central_register_port
        self.central_register_ip = central_register_ip
        self.client_name = client_name
        self.block_update_queues = block_update_queues
        self.block_chain = block_chain
        self.sock = sock
        self.threadID = threadID
        self.name = name

    def run(self):
        print "listeningThread for client '{0}' is active".format(self.client_name)
        while True:

            # listen for new messages
            data, addr = self.sock.recvfrom(4096)
            print "client received data from address" + str(addr)
            print str(self.central_register_ip == addr[0])
            print str(self.central_register_port == addr[1])
            # check if it is a new client
            if (self.central_register_ip == addr[0] and self.central_register_port == addr[1]):
                self.client_dict_lock.acquire()
                self.client_dict[data[0]] = (data[1], RSA.importKey(data[2]))
                self.client_dict_lock.release()
                print "new client registered"
            else:
                deserialized_block = pickle.loads(data)
                new_block_verified = ProofOfWork.verify_next_block_in_chain(deserialized_block, self.block_chain)
                if new_block_verified:
                    block_added = self.block_chain.add_block(deserialized_block)
                    if block_added:
                        print "Block number {0} was added to the block chain by client '{1}'".format(
                            str(deserialized_block.get_counter()), deserialized_block.get_data())
                        for queue in self.block_update_queues:
                            next_block = create_next_block(self.block_chain, "will_be_updated_by_client")
                            queue.put(next_block)
                    else:
                        print "Something went wrong. Could not add block to chain"
                else:
                    print "Got a proposed new block but it did not verify"


class calculationThread(threading.Thread):
    def __init__(self, threadID, name, sock, block_without_nonce, client_name, block_update_queue, client_dict_lock,
                 client_dict):
        threading.Thread.__init__(self)
        self.client_dict = client_dict
        self.client_dict_lock = client_dict_lock
        self.sock = sock
        self.block_update_queue = block_update_queue
        self.client_name = client_name
        self.threadID = threadID
        self.name = name
        self.block = block_without_nonce

    def run(self):
        print "calculationThread-{0} for client '{1}' is active".format(self.threadID, self.client_name)
        while True:
            for i in range(1000):
                found_nonce = ProofOfWork.try_to_set_correct_nonce(self.block)
                if found_nonce:
                    # Check if somebody else already found the next block
                    someone_already_found_block = not self.block_update_queue.empty()
                    if not someone_already_found_block:
                        print "Thread {0} found a nonce and thinks its the first one !".format(
                            self.threadID)
                        # Broadcast the block
                        self.client_dict_lock.acquire()
                        serialized_block = pickle.dumps(self.block)
                        print "client_dict: " + str(self.client_dict)
                        for c in self.client_dict:
                            self.sock.sendto(serialized_block, self.client_dict[c][0])
                        self.client_dict_lock.release()
                        self.update_block()
                        continue
                    else:
                        # Found a block but someone was faster :(
                        print "Thread {0} from client {1} found a nonce but was too slow".format(self.threadID,
                                                                                                 self.client_name)
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
    hash_difficulty_value = 20
    block = Block(prev_block.get_hash_value(), timestamp, data, new_counter, hash_difficulty_value)

    return block


def run(client_name, client_ip, client_port, central_register_ip, central_register_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((client_ip, client_port))

    client_dict = {}

    key = RSAWrapper.keygen()
    pub_key = key.publickey()
    ID = Common.client_id_from_public_key(pub_key)

    client_dict[ID] = ((client_ip, client_port), pub_key)
    serialized_message = pickle.dumps((ID, (client_ip, client_port), pub_key))
    sock.sendto(serialized_message, (central_register_ip, central_register_port))

    client_dict_lock = threading.Lock()

    block_chain = BlockChain()
    block_without_nonce1 = create_next_block(block_chain, client_name)
    block_without_nonce2 = create_next_block(block_chain, client_name)
    block_without_nonce3 = create_next_block(block_chain, client_name)

    queue1 = Queue.Queue()
    queue2 = Queue.Queue()
    queue3 = Queue.Queue()

    listen = listeningThread(0, "Listening_Thread", sock, block_chain, client_name, [queue1, queue2, queue3],
                             central_register_ip,
                             central_register_port,
                             client_dict)
    calc_1 = calculationThread(1, "Calculation_Thread", sock, block_without_nonce1, client_name, queue1,
                               client_dict_lock,
                               client_dict)
    calc_2 = calculationThread(2, "Calculation_Thread", sock, block_without_nonce2, client_name, queue2,
                               client_dict_lock,
                               client_dict)
    calc_3 = calculationThread(3, "Calculation_Thread", sock, block_without_nonce3, client_name, queue3,
                               client_dict_lock,
                               client_dict)

    # Threads set in daemon mode so that they die when the main process dies
    listen.daemon = True
    listen.start()

    calc_1.daemon = True
    calc_2.daemon = True
    calc_3.daemon = True
    calc_1.start()
    calc_2.start()
    calc_3.start()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    try:
        client_name = sys.argv[1]
        client_ip = sys.argv[2]
        client_port = int(sys.argv[3])
        central_register_ip = sys.argv[4]
        central_register_port = int(sys.argv[5])
        run(client_name, client_ip, client_port, central_register_ip, central_register_port)
    except:
        message = """Usage: python Working_Client.py client_name client_ip client_port central_register_ip central_register_port
         Example: python Working_Client.py AwesomeClient localhost 10500 localhost 10550
         """

        print message
        sys.exit()

