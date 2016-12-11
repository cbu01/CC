from Block import Block


class BlockChain:
    def __init__(self):
        self.latest_block = None
        self.blocks_dictionary = {}  # {BLockHashId: Block}
        self.genesis_block_hash = None
        self.genesis_block_hash_pointer = "GENESIS_BLOCK_HASH_POINTER"
        self._init_genesis_block()

    def _init_genesis_block(self):
        timestamp = 0
        counter = 1
        difficulty_level = 0
        genesis_block = Block(self.genesis_block_hash_pointer, timestamp, "GENESIS_BLOCK", counter, difficulty_level)
        genesis_block.set_nonce("")
        self.genesis_block_hash = genesis_block.get_hash_value()
        self.blocks_dictionary[self.genesis_block_hash] = genesis_block
        self.latest_block = genesis_block

    def add_block(self, block):
        """ Add a new block to the chain if it's hash matches and it's hash pointer points to the current block

        :param block : (Block) the new block
        :return: (bool) True if block added successfully, False otherwise
        """
        if not block.has_valid_hash_value():
            print "Wrong hash value for block"
            return False

        block_hash_pointer_val = block.get_previous_block_hash()
        if block_hash_pointer_val not in self.blocks_dictionary:
            return False

        latest_block_hash = self.latest_block.get_hash_value()
        if block_hash_pointer_val != latest_block_hash:
            print "Hash pointer of new block does not match hash value of latest block"
            return False

        block_own_hash_value = block.get_hash_value()
        if block_own_hash_value in self.blocks_dictionary:
            print "Block has already been added to block chain"
            return False

        self.blocks_dictionary[block_own_hash_value] = block
        self.latest_block = block
        return True

    def get_latest_block(self):
        return self.latest_block

    def audit(self):
        current_block = self.latest_block

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
