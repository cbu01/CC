from Block import Block
import collections
import time


class BlockChain:
    def __init__(self):
        self.first_non_genesis_block = None
        self.hash_difficulty_level = None
        self.block_safety_offset = 5  # The number of blocks from the latest blocks that is considered 'safe'
        self.latest_blocks = []
        self.blocks_dictionary = {}  # {BLockHashId: Block}
        self.genesis_block_hash = None
        self.genesis_block_hash_pointer = "GENESIS_BLOCK_HASH_POINTER"
        self.fork_record = []  # List of int tuples that show (start_counter_of_fork, end_counter_of_fork)
        self.current_fork = None
        self._init_genesis_block()

    def get_hash_difficulty_level(self):
        return self.hash_difficulty_level

    def set_hash_difficulty_level(self, hash_difficulty_level):
        self.hash_difficulty_level = hash_difficulty_level

    def get_first_non_genesis_block(self):
        return self.first_non_genesis_block

    def has_fork(self):
        return self.current_fork is not None

    def get_fork_record(self):
        return_list = list(self.fork_record)  # To copy and not mess with self list
        if self.current_fork is not None:
            return_list.append((self.current_fork, self.get_target_block().get_counter()))
        return return_list

    def get_number_of_blocks(self):
        return len(self.blocks_dictionary)

    def get_number_of_blocks_from_client(self, client_data_content):
        return len([block for block in self.blocks_dictionary.values() if block.get_data() == client_data_content])

    def get_latest_safe_block_hash_id(self):
        """ Gets the hash id of the latest block that is considered safe. Controlled by self.block_safety_offset """
        latest_current_block = self.latest_blocks[0]
        for i in range(self.block_safety_offset):
            if latest_current_block.get_hash_value() == self.genesis_block_hash:
                return latest_current_block.get_hash_value()
            latest_current_block = self.blocks_dictionary[latest_current_block.get_previous_block_hash()]

        return latest_current_block.get_hash_value()

    def add_block_to_latest_blocks(self, new_block):
        # Remove blocks that have a lower counter then new_counter - 1
        new_counter = new_block.get_counter()
        self.latest_blocks = [late_block for late_block in self.latest_blocks if late_block.get_counter() >= new_counter - 1]

        self.latest_blocks.append(new_block)

        # A block chain has a fork if it contains multiple latest blocks with the same counter
        if self.current_fork is None:
            # Check if we just created a fork
            list_of_counters = [block.get_counter() for block in self.latest_blocks]
            duplicate_counters = [item for item, count in collections.Counter(list_of_counters).items() if count > 1]

            if len(duplicate_counters) > 0:
                self.current_fork = duplicate_counters[0]
        else:
            # There was a fork. Check if there is not fork anymore
            list_of_counters = [block.get_counter() for block in self.latest_blocks]
            duplicate_counters = [item for item, count in collections.Counter(list_of_counters).items() if count > 1]

            if len(duplicate_counters) == 0:
                self.fork_record.append((self.current_fork, new_counter))
                self.current_fork = None

    def _init_genesis_block(self):
        timestamp = 0
        counter = 1
        difficulty_level = 0
        genesis_block = Block(self.genesis_block_hash_pointer, timestamp, "GENESIS_BLOCK", counter, difficulty_level)
        genesis_block.set_nonce("")
        self.genesis_block_hash = genesis_block.get_hash_value()
        self.blocks_dictionary[self.genesis_block_hash] = genesis_block
        self.latest_blocks = [genesis_block]

    def add_blocks_from_another_chain(self, list_of_blocks):
        """ Tries to add a list of blocks to the current chain. If any block does not verify
            or if no block matches any of the current latest blocks, this fails and method returns False.
            Otherwise returns True
        """

        # Start by removing all the blocks we already have
        list_of_blocks = [x for x in list_of_blocks if x.get_hash_value() not in self.blocks_dictionary]

        while len(list_of_blocks) > 0:
            next_block_to_add = None
            latest_blocks_hash_values = [x.get_hash_value() for x in self.latest_blocks]
            for block in list_of_blocks:
                if block.get_previous_block_hash() in latest_blocks_hash_values:
                    next_block_to_add = block
                    continue

            if next_block_to_add is not None:
                block_added = self.add_block(next_block_to_add)
                if block_added:
                    list_of_blocks.remove(next_block_to_add)
                else:
                    print "Error adding block"
                    return False

        return True

    def add_block(self, block):
        """ Add a new block to the chain if it's hash matches and it's hash pointer points to any of the current blocks

        :param block : (Block) the new block
        :return: (bool) True if block added successfully, False otherwise
        """
        if not block.has_valid_hash_value():
            print "Wrong hash value for block"
            return False

        block_hash_pointer_val = block.get_previous_block_hash()
        if block_hash_pointer_val not in self.blocks_dictionary:
            return False

        hash_pointer_to_latest_block_found = False
        for late_block in self.latest_blocks:
            latest_block_hash = late_block.get_hash_value()
            if block_hash_pointer_val == latest_block_hash:
                hash_pointer_to_latest_block_found = True

        if not hash_pointer_to_latest_block_found:
            print "Hash pointer of new block does not match hash value of any latest block"
            return False

        block_own_hash_value = block.get_hash_value()
        if block_own_hash_value in self.blocks_dictionary:
            print "Block has already been added to block chain"
            return False

        if len(self.blocks_dictionary) == 1:
            self.first_non_genesis_block = block

        self.blocks_dictionary[block_own_hash_value] = block
        self.add_block_to_latest_blocks(block)
        return True

    def get_blocks_since_hash_id(self, hash_id):
        """ Returns a list of blocks from the current target block until the given hash_id is reached
            (excluding the block with the given hash id). The blocks are returned in the order they should be added """
        return_list = []
        current_block = self.get_target_block()
        while current_block.get_hash_value() != hash_id:
            if current_block.get_hash_value() == self.genesis_block_hash:
                print "The given hash id does not exist in the block chain"
                return []

            return_list.append(current_block)

            current_block = self.blocks_dictionary[current_block.get_previous_block_hash()]
        return return_list[::-1]

    def get_target_block(self):
        """ Returns a block that a client should be working to add to.
        This is a randomly chosen block of the highest counter blocks """
        max_counter = max(block.get_counter() for block in self.latest_blocks)
        max_counter_blocks = [block for block in self.latest_blocks if block.get_counter() == max_counter]
        return max_counter_blocks[0]

    def get_target_blocks(self):
        return self.latest_blocks

    def audit(self):
        current_block = self.latest_blocks[0]

        while current_block.get_previous_block_hash() != self.genesis_block_hash_pointer:
            valid_internal_hash = current_block.has_valid_hash_value()
            if not valid_internal_hash:
                print "Invalid internal hash value"
                return False

            current_block_hash_pointer = current_block.get_previous_block_hash()
            if current_block_hash_pointer not in self.blocks_dictionary:
                print "Can't find previous block by hash pointer "
                return False

            previous_block = self.blocks_dictionary[current_block_hash_pointer]
            previous_block_hash = previous_block.get_hash_value()

            if current_block_hash_pointer != previous_block_hash:
                print "Hash pointer values do not match"
                return False

            current_block = previous_block

        return True
