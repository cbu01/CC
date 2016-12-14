from Block import Block


class BlockChain:
    def __init__(self):
        self.block_safety_offset = 3  # The number of blocks from the latest blocks that is considered 'safe'
        self.latest_blocks = []
        self.blocks_dictionary = {}  # {BLockHashId: Block}
        self.genesis_block_hash = None
        self.genesis_block_hash_pointer = "GENESIS_BLOCK_HASH_POINTER"
        self._init_genesis_block()

    def get_number_of_blocks(self):
        return len(self.blocks_dictionary)

    def get_latest_safe_block_hash_id(self):
        """ Gets the hash id of the latest block that is considered safe. Controlled by self.block_safety_offset """
        latest_current_block = self.latest_blocks[0]
        for i in range(self.block_safety_offset):
            if latest_current_block.get_hash_value() == self.genesis_block_hash:
                return latest_current_block.get_hash_value()
            latest_current_block = self.blocks_dictionary[latest_current_block.get_previous_block_hash()]

        return latest_current_block.get_hash_value()

    def add_block_to_latest_blocks(self, new_block):
        # Remove blocks that the new block points to from latest blocks list
        new_block_hash_pointer = new_block.get_previous_block_hash()
        if new_block_hash_pointer in self.blocks_dictionary:
            previous_block = self.blocks_dictionary[new_block_hash_pointer]
            if previous_block in self.latest_blocks:
                self.latest_blocks.remove(previous_block)
        else:
            raise Exception("Trying to add new block to latest blocks but it's not pointing to anything in the chain !")

        # Remove blocks that have a lower counter then new_counter - 1
        new_counter = new_block.get_counter()
        self.latest_blocks = [late_block for late_block in self.latest_blocks if late_block.get_counter() < new_counter - 1]

        self.latest_blocks.append(new_block)
        pass

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
        """ Returns a block that a client should be working to add to """
        return self.latest_blocks[0]

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
