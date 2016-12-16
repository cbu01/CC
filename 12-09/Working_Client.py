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
import math

REQUEST_BLOCKS = "REQUEST_BLOCKS"
DISCOVERED_BLOCK = "DISCOVERED_BLOCK"
FINISHED_SENDING_REQUESTED_BLOCKS = "FINISHED_SENDING_REQUESTED_BLOCKS"
INCOMING_BLOCK_FROM_OUR_REQUEST = "INCOMING_BLOCK_FROM_OUR_REQUEST"


class listeningThread(threading.Thread):
    def __init__(self,
                 client_id,
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
                 client_dict,
                 run_mode,
                 run_mode_data,
                 minimum_hash_difficulty_level,
                 maximum_hash_difficulty_level):
        threading.Thread.__init__(self)
        self.client_id = client_id
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
        self.minimum_hash_difficulty_level = minimum_hash_difficulty_level
        self.maximum_hash_difficulty_level = maximum_hash_difficulty_level

        # 0 = normal[default], 1 = average_block_find_time, 2 = equal_num_blocks_per_client
        self.run_mode = run_mode
        self.run_mode_data = run_mode_data  # Used if run_mode is 1 for num seconds

    def run(self):
        try:
            waiting_for_blocks_from_client = False

            while True:
                # listen for new messages
                data, addr = self.sock.recvfrom(4096)
                deserialized_data = pickle.loads(data)

                command = deserialized_data[0]

                if self.central_register_ip == addr[0] and self.central_register_port == addr[1]:
                    # New client

                    self.client_dict_lock.acquire()
                    self.client_dict[deserialized_data[0]] = (deserialized_data[1], RSA.importKey(deserialized_data[2]))
                    self.client_dict_lock.release()
                elif command == REQUEST_BLOCKS:
                    print "Got a request for blocks in my block chain"
                    hash_id_from_request = deserialized_data[1]
                    blocks_to_respond_with = self.block_chain.get_blocks_since_hash_id(hash_id_from_request)
                    for block in blocks_to_respond_with:
                        msg = pickle.dumps((INCOMING_BLOCK_FROM_OUR_REQUEST, block))
                        self.sock.sendto(msg, addr)

                    # Send messages that we are done sending blocks
                    msg = pickle.dumps((FINISHED_SENDING_REQUESTED_BLOCKS, ""))
                    self.sock.sendto(msg, addr)
                    print "Finished sending blocks to client"
                elif command == INCOMING_BLOCK_FROM_OUR_REQUEST:
                    sent_block = deserialized_data[1]
                    # print "Got block number {0} from the other client".format(sent_block.get_counter())
                    self.block_chain.add_blocks_from_another_chain([sent_block])
                    # print "After adding my block chain has {0} blocks".format(self.block_chain.get_number_of_blocks())
                elif command == FINISHED_SENDING_REQUESTED_BLOCKS:
                    # New block for calculation threads
                    current_latest_counter = self.block_chain.get_target_block().get_counter()
                    print "Finished receiving blocks from other client. Current latest block chain counter is " + str(
                        current_latest_counter)
                    for queue in self.block_update_queues:
                        next_block = create_next_block(self.block_chain, "will_be_updated_by_client")
                        queue.put(next_block)

                    # Remove stop condition so calculation threads can restart their work
                    for stop_queue in self.stop_work_queues:
                        stop_queue.get()

                    waiting_for_blocks_from_client = False
                elif command == DISCOVERED_BLOCK:
                    if waiting_for_blocks_from_client:
                        continue
                    received_block = deserialized_data[1]
                    received_block_counter = received_block.get_counter()
                    target_block_counter = self.block_chain.get_target_block().get_counter()

                    block_has_too_low_counter = received_block_counter < target_block_counter
                    if block_has_too_low_counter:
                        print "We got an older block. Our latest block counter is {0} but the new blocks counter " \
                              "is {1}. So we ignore it".format(target_block_counter, received_block_counter)
                        continue

                    block_has_too_high_counter = received_block_counter > target_block_counter + 1
                    if block_has_too_high_counter:
                        print "Got a higher block counter than expected. Expected counter is {0} but we got {1}. " \
                              "Maybe we are out of sync, so lets call some client and get his/her latest block chain". \
                            format(target_block_counter + 1, received_block_counter)

                        # Try to nuke the block chain and send the genesis hash
                        # to collect a fresh block chain from another client
                        previous_hash_difficulty_level = self.block_chain.get_hash_difficulty_level()
                        self.block_chain = BlockChain()
                        self.block_chain.set_hash_difficulty_level(previous_hash_difficulty_level)
                        hash_id = self.block_chain.get_latest_safe_block_hash_id()
                        waiting_for_blocks_from_client = True
                        self.request_block_chain_from_random_client(hash_id)
                        continue

                    new_block_verified = ProofOfWork.verify_next_block_in_chain(received_block, self.block_chain)
                    if new_block_verified:
                        block_added = self.block_chain.add_block(received_block)
                        if block_added:
                            print "Block number {0} was added to the block chain by client '{1}'".format(
                                str(received_block.get_counter()), received_block.get_data())

                            if self.run_mode == 1:
                                # We want the average number of seconds per block to be self.run_mode_data
                                # If we are below that number we increase the difficulty
                                # If we are above that number we decrease the difficulty
                                number_of_blocks = self.block_chain.get_number_of_blocks()
                                if number_of_blocks > 2:
                                    total_seconds_passed = last_block.get_time_stamp() - first_block.get_time_stamp()
                                    first_block = self.block_chain.get_first_non_genesis_block()
                                    last_block = received_block

                                    average_time_per_block = float(total_seconds_passed)/number_of_blocks

                                    distance_from_time_target = average_time_per_block - self.run_mode_data
                                    if math.fabs(distance_from_time_target) < 1:
                                        # Lets not do anything if difference is within one sec
                                        pass
                                    elif average_time_per_block > self.run_mode_data:
                                        # Decrease difficulty
                                        current_hash_level_difficulty = self.block_chain.get_hash_difficulty_level()

                                        if current_hash_level_difficulty > self.minimum_hash_difficulty_level:
                                            self.block_chain.set_hash_difficulty_level(current_hash_level_difficulty - 1)
                                            print "This is too difficult (Average time between blocks is {0} sec). Lets decrease the hash difficulty from {1} to {2}"\
                                                .format(int(average_time_per_block),current_hash_level_difficulty, current_hash_level_difficulty - 1)
                                    else:
                                        # Increase difficulty
                                        current_hash_level_difficulty = self.block_chain.get_hash_difficulty_level()
                                        if current_hash_level_difficulty < self.maximum_hash_difficulty_level:
                                            self.block_chain.set_hash_difficulty_level(current_hash_level_difficulty + 1)
                                            print "This is too easy (Average time between blocks is {0} sec). Lets increase the hash difficulty from {1} to {2}" \
                                                .format(int(average_time_per_block), current_hash_level_difficulty,
                                                        current_hash_level_difficulty + 1)
                            elif self.run_mode == 2:
                                # We want every client to on average have as many blocks as everybody else
                                num_clients = len(self.client_dict)
                                if num_clients > 1:
                                    num_blocks_in_chain = self.block_chain.get_number_of_blocks()
                                    num_block_from_me = self.block_chain.get_number_of_blocks_from_client(self.client_name)
                                    client_ratio = 1 / float(num_clients)
                                    client_block_ratio = num_block_from_me / float(num_blocks_in_chain)

                                    if math.fabs(client_ratio - client_block_ratio) < 0.1:
                                        # If we are within 10% we do no change
                                        pass
                                    elif client_ratio > client_block_ratio:
                                        # This is too hard for this client, he needs more blocks !
                                        current_hash_level_difficulty = self.block_chain.get_hash_difficulty_level()
                                        if current_hash_level_difficulty > self.minimum_hash_difficulty_level:
                                            self.block_chain.set_hash_difficulty_level(current_hash_level_difficulty - 1)
                                            print "Client only has a {0:.2f} share of the blocks ({3} client blocks). Lets decrease its hash difficulty from {1} to {2}" \
                                                .format(client_block_ratio, current_hash_level_difficulty,
                                                        current_hash_level_difficulty - 1, num_block_from_me)
                                    else:
                                        # This is too easy for this client, he needs less blocks !
                                        current_hash_level_difficulty = self.block_chain.get_hash_difficulty_level()
                                        if current_hash_level_difficulty < self.maximum_hash_difficulty_level:
                                            self.block_chain.set_hash_difficulty_level(current_hash_level_difficulty + 1)
                                            print "Client has a {0:.2f} share of the blocks ({3} client blocks). Lets increase its hash difficulty from {1} to {2}" \
                                                .format(client_block_ratio, current_hash_level_difficulty,
                                                        current_hash_level_difficulty + 1, num_block_from_me)

                            for queue in self.block_update_queues:
                                next_block = create_next_block(self.block_chain, "will_be_updated_by_client")
                                queue.put(next_block)
                        else:
                            print "Something went wrong. Could not add block to chain"
                    else:
                        print "Got a proposed new block but it did not verify"
        except Exception as e:
            print str(e)

    def request_block_chain_from_random_client(self, parent_block_hash_id):
        """
        :param parent_block_hash_id: The hash id of the last block that should not be included.
                                     Every block after should be sent
        """

        print "Sending requests for the latest blocks in the chain"
        for stop_queue in self.stop_work_queues:
            stop_queue.put(True)

        # Pick the first client that is not us
        for key, client in self.client_dict.items():
            if key != self.client_id:
                client_address = client[0]
                msg = pickle.dumps((REQUEST_BLOCKS, parent_block_hash_id))
                self.sock.sendto(msg, client_address)
                return


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
                        # print "Thread {0} found a nonce and thinks its the first one !".format(
                        #     self.threadID)

                        if not self.stop_work_queue.empty():
                            print "O No ! The listener thread asked us to stop working. " \
                                  "Lets not even try to broadcast the newly found block"
                            break

                        # Broadcast the block
                        self.client_dict_lock.acquire()
                        serialized_block = pickle.dumps((DISCOVERED_BLOCK, self.block))

                        for c in self.client_dict:
                            self.sock.sendto(serialized_block, self.client_dict[c][0])
                        self.client_dict_lock.release()
                        self.update_block()
                        continue
                    else:
                        # Found a block but someone was faster :(
                        # print "Thread {0} from client {1} found a nonce but was too slow".format(self.threadID, self.client_name)
                        self.update_block()
                        continue

            # if not self.stop_work_queue.empty():
            #     print "Calculation thread was asked to stop working"

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
    hash_difficulty_value = block_chain.get_hash_difficulty_level()
    block = Block(prev_block.get_hash_value(), timestamp, data, new_counter, hash_difficulty_value)

    return block


def run(client_name, client_ip, client_port, central_register_ip, central_register_port, hash_difficulty_level, run_mode, run_mode_data):
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
    block_chain.set_hash_difficulty_level(hash_difficulty_level)
    block_without_nonce1 = create_next_block(block_chain, client_name)
    block_without_nonce2 = create_next_block(block_chain, client_name)
    block_without_nonce3 = create_next_block(block_chain, client_name)

    block_update_queue1 = Queue.Queue()
    block_update_queue2 = Queue.Queue()
    block_update_queue3 = Queue.Queue()

    stop_calculation_queue1 = Queue.Queue()
    stop_calculation_queue2 = Queue.Queue()
    stop_calculation_queue3 = Queue.Queue()

    minimum_hash_difficulty_level = 12
    maximum_hash_difficulty_level = 24

    if hash_difficulty_level > maximum_hash_difficulty_level:
        print "The max hash difficulty level is 24. This is for your own sanity (unless you really like waiting)"

    listen = listeningThread(ID, 0, "Listening_Thread", sock, block_chain, client_name,
                             [block_update_queue1, block_update_queue2, block_update_queue3],
                             [stop_calculation_queue1, stop_calculation_queue2, stop_calculation_queue3],
                             central_register_ip,
                             central_register_port,
                             client_dict_lock,
                             client_dict,
                             run_mode, run_mode_data, minimum_hash_difficulty_level, maximum_hash_difficulty_level)
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

    run_mode_description = "Normal"
    if run_mode == 1:
        run_mode_description = "'Average time between blocks should be {0} seconds'".format(run_mode_data)
    elif run_mode == 2:
        run_mode_description = "'Every client should get equal amount of blocks'"

    print "Client {0} started in {1} mode with initial difficulty {2}".format(client_name, run_mode_description, hash_difficulty_level)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    try:
        client_name = sys.argv[1]
        client_ip = sys.argv[2]
        client_port = int(sys.argv[3])
        central_register_ip = sys.argv[4]
        central_register_port = int(sys.argv[5])
        difficulty_level = int(sys.argv[6])
        run_mode = 0
        run_mode_data = 0
        try:
            run_mode = int(sys.argv[7])
            if run_mode == 1:
                run_mode_data = int(sys.argv[8])
        except:
            run_mode = 0
            run_mode_data = 0
        run(client_name, client_ip, client_port, central_register_ip, central_register_port, difficulty_level, run_mode, run_mode_data)
    except Exception as e:
        message = """Usage: python Working_Client.py client_name client_ip client_port central_register_ip central_register_port start_difficulty_level run_option_flag (0 = normal [default], 1 = average_block_find_time, 2 = equal_num_blocks_per_client)  run_option_seconds (only if run_option_flag == 1)
         Example 1: python Working_Client.py AwesomeClient localhost 10500 localhost 10550 20
         Example 2: python Working_Client.py AwesomeClient localhost 10500 localhost 10550 20 1 10
         Example 3: python Working_Client.py AwesomeClient localhost 10500 localhost 10550 20 2
         """

        print message
        sys.exit()
