from Block import Block


class BlockChain:
    def __init__(self):
        self.latest_block = None
        self.genesis_block_hash = None
        self._init_genesis_block()

    def _init_genesis_block(self):
        timestamp = 0
        counter = 1
        difficulty_level = 0
        genesis_block = Block(None, "PREV_HASH", timestamp, "GENESIS_BLOCK", counter, difficulty_level)
        genesis_block.set_nonce("")
        self.latest_block = genesis_block
        self.genesis_block_hash = genesis_block.get_hash_value()

    def add_block(self, block):
        """ Add a new block to the chain if it's hash matches and it's hash pointer points to the current block

        :param block : (Block) the new block
        :return:
        """
        if not block.has_valid_hash_value():
            print "Wrong hash value for block"
            return False

        block_hash_pointer_val = block.get_previous_block_hash()
        latest_block_hash = self.latest_block.get_hash_value()
        if block_hash_pointer_val != latest_block_hash:
            print "Hash pointer of new block does not match hash value of latest block"
            return False

        self.latest_block = block
        return True

    def get_latest_block(self):
        return self.latest_block

    def audit(self):
        current_block = self.latest_block

        while current_block.get_previous_block() is not None:
            valid_internal_hash = current_block.has_valid_hash_value()
            if not valid_internal_hash:
                print "Invalid internal hash value"
                return False

            current_block_hash_pointer = current_block.get_previous_block_hash()
            previous_block_hash = current_block.get_previous_block().get_hash_value()

            if current_block_hash_pointer != previous_block_hash:
                print "Hash pointer values do not match"
                return False

            current_block = current_block.get_previous_block()

        return True
