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
                 stop_work_queues,
                 central_register_ip,
                 central_register_port,
                 client_dict_lock,
                 client_dict):
        threading.Thread.__init__(self)
        self.stop_work_queues = stop_work_queues
        self.client_dict = client_dict
        self.client_dict_lock = client_dict_lock
        self.central_register_port = central_register_port
        self.central_register_ip = central_register_ip
        self.client_name = client_name
        self.block_update_queues = block_update_queues
        self.block_chain = block_chain
        self.sock = sock
        self.threadID = threadID
        self.name = name


    # TODO Mannsi - Client needs to somehow try to get the initial version of the block chain when he starts (unless he is the only client of course)
    def run(self):
        while True:
            # listen for new messages
            data, addr = self.sock.recvfrom(4096)
            deserialized_data = pickle.loads(data)

            # TODO these are just placeholders so that I can code the below if statements.
            # These are the parameters that will be sent in the request_block_chain_from_random_client() function below
            INCOMING_REQUEST_FOR_BLOCKS = False
            HASH_ID_FROM_REQUEST = ""

            # TODO again these are just placeholder parameters since I don't know how this will be sent exactly
            # These are the parameters sent in the INCOMING_REQUEST_FOR_BLOCKS if block below
            INCOMING_BLOCK_FROM_OUR_REQUEST = False
            THE_BLOCK_SENT = None

            FINISHED_SENDING_REQUESTED_BLOCKS = False

            if self.central_register_ip == addr[0] and self.central_register_port == addr[1]:
                # New client

                self.client_dict_lock.acquire()
                self.client_dict[deserialized_data[0]] = (deserialized_data[1], RSA.importKey(deserialized_data[2]))
                self.client_dict_lock.release()
            elif INCOMING_REQUEST_FOR_BLOCKS:
                # Received request for blocks in our block chain
                blocks_to_respond_with = self.block_chain.get_blocks_since_hash_id(HASH_ID_FROM_REQUEST)
                for block in blocks_to_respond_with:
                    # TODO Caroline send block to the client that sent this request to us
                    pass
                # TODO send to the same client that we are finished sending blocks
            elif INCOMING_BLOCK_FROM_OUR_REQUEST:
                self.block_chain.add_blocks_from_another_chain([THE_BLOCK_SENT])
            elif FINISHED_SENDING_REQUESTED_BLOCKS:
                # New block for calculation threads
                for queue in self.block_update_queues:
                    next_block = create_next_block(self.block_chain, "will_be_updated_by_client")
                    queue.put(next_block)

                # Remove stop condition so calculation threads can restart their work
                for stop_queue in self.stop_work_queues:
                    stop_queue.get()
                pass
            else:
                # Received newly discovered block
                received_block = deserialized_data

                received_block_counter = received_block.get_counter()
                target_block_counter = self.block_chain.get_target_block().get_counter()

                block_has_too_low_counter = received_block_counter < target_block_counter
                if block_has_too_low_counter:
                    print "We got an older block. Our latest block counter is {0} but the new blocks counter is {1}".\
                        format(target_block_counter, received_block_counter)
                    continue

                block_has_too_high_counter = received_block_counter > target_block_counter + 1
                if block_has_too_high_counter:
                    print "Got a higher block counter than expected. Expected counter is {0} but we got {1}. " \
                          "Maybe we are out of sync, so lets call some client and get his/her latest block chain".\
                        format(target_block_counter + 1, received_block_counter)
                    hash_id = self.block_chain.get_latest_safe_block_hash_id()
                    self.request_block_chain_from_random_client(hash_id)
                    continue

                new_block_verified = ProofOfWork.verify_next_block_in_chain(received_block, self.block_chain)
                if new_block_verified:
                    block_added = self.block_chain.add_block(received_block)
                    if block_added:
                        print "Block number {0} was added to the block chain by client '{1}'".format(
                            str(received_block.get_counter()), received_block.get_data())
                        for queue in self.block_update_queues:
                            next_block = create_next_block(self.block_chain, "will_be_updated_by_client")
                            queue.put(next_block)
                    else:
                        print "Something went wrong. Could not add block to chain"
                else:
                    print "Got a proposed new block but it did not verify"

    def request_block_chain_from_random_client(self, hash_id):
        for stop_queue in self.stop_work_queues:
            stop_queue.put(True)
        # TODO Caroline send request to a random client asking for blocks using the above hash_id as parameter


class calculationThread(threading.Thread):
    def __init__(self, threadID,
                 name,
                 sock,
                 block_without_nonce,
                 client_name,
                 block_update_queue,
                 stop_work_queue,
                 client_dict_lock,
                 client_dict):
        threading.Thread.__init__(self)
        self.stop_work_queue = stop_work_queue  # If this queue is non-empty, stop work
        self.client_dict = client_dict
        self.client_dict_lock = client_dict_lock
        self.sock = sock
        self.block_update_queue = block_update_queue
        self.client_name = client_name
        self.threadID = threadID
        self.name = name
        self.block = block_without_nonce

    def run(self):
        while True:
            for i in range(1000):
                found_nonce = ProofOfWork.try_to_set_correct_nonce(self.block)
                if found_nonce:
                    # Check if somebody else already found the next block
                    someone_already_found_block = not self.block_update_queue.empty()
                    if not someone_already_found_block:
                        print "Thread {0} found a nonce and thinks its the first one !".format(
                            self.threadID)

                        if not self.stop_work_queue.empty():
                            print "O No ! The listener thread asked us to stop working. " \
                                  "Lets not even try to broadcast the newly found block"
                            break

                        # Broadcast the block
                        self.client_dict_lock.acquire()
                        serialized_block = pickle.dumps(self.block)

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

            if not self.stop_work_queue.empty():
                print "Calculation thread was asked to stop working"

            while not self.stop_work_queue.empty():
                time.sleep(0.01)
            self.update_block()

    def update_block(self):
        if not self.block_update_queue.empty():
            self.block = self.block_update_queue.get()
            self.block.data = self.client_name


def create_next_block(block_chain, client_name):
    prev_block = block_chain.get_target_block()
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
    serialized_message = pickle.dumps((ID, (client_ip, client_port), pub_key.exportKey()))
    sock.sendto(serialized_message, (central_register_ip, central_register_port))

    client_dict_lock = threading.Lock()

    block_chain = BlockChain()
    block_without_nonce1 = create_next_block(block_chain, client_name)
    block_without_nonce2 = create_next_block(block_chain, client_name)
    block_without_nonce3 = create_next_block(block_chain, client_name)

    block_update_queue1 = Queue.Queue()
    block_update_queue2 = Queue.Queue()
    block_update_queue3 = Queue.Queue()

    stop_calculation_queue1 = Queue.Queue()
    stop_calculation_queue2 = Queue.Queue()
    stop_calculation_queue3 = Queue.Queue()

    listen = listeningThread(0, "Listening_Thread", sock, block_chain, client_name,
                             [block_update_queue1, block_update_queue2, block_update_queue3],
                             [stop_calculation_queue1, stop_calculation_queue2, stop_calculation_queue3],
                             central_register_ip,
                             central_register_port,
                             client_dict_lock,
                             client_dict)
    calc_1 = calculationThread(1, "Calculation_Thread", sock, block_without_nonce1, client_name, block_update_queue1,
                               stop_calculation_queue1,
                               client_dict_lock,
                               client_dict)
    calc_2 = calculationThread(2, "Calculation_Thread", sock, block_without_nonce2, client_name, block_update_queue2,
                               stop_calculation_queue2,
                               client_dict_lock,
                               client_dict)
    calc_3 = calculationThread(3, "Calculation_Thread", sock, block_without_nonce3, client_name, block_update_queue3,
                               stop_calculation_queue3,
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

    print "Client {0} started".format(client_name)

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

