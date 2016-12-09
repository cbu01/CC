import Block


class BlockChain:
    def __init__(self):
        self.latest_block = None
        self.genesis_block_hash = None
        self._init_genesis_block()

    def _init_genesis_block(self):
        genesis_block = Block(None, "", 0, "", 1, 0)
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

        block_hash_pointer_val = block.get_hash_pointer_value()
        latest_block_hash = self.latest_block.get_hash_value()
        if block_hash_pointer_val != latest_block_hash:
            print "Hash pointer of new block does not match hash value of latest block"
            return False

        self.latest_block = block
        return True
