import hashlib
import ProofOfWork


class Block:
    def __init__(self,
                 previous_block_hash,
                 timestamp,
                 data,
                 counter,
                 hash_difficulty_value):
        self.previous_block_hash = previous_block_hash
        self.timestamp = timestamp
        self.data = data
        self.counter = counter
        self.hash_difficulty_value = hash_difficulty_value
        self.nonce = None

    def set_nonce(self, nonce):
        self.nonce = nonce

    def get_hash_value(self):
        """ Returns the hash value of the block

        :return str: hash value of the block
        """
        if self.nonce is None:
            return None

        hash_string = self.previous_block_hash
        hash_string += str(self.timestamp)
        hash_string += str(self.data)
        hash_string += str(self.counter)
        hash_string += str(self.hash_difficulty_value)
        hash_string += str(self.nonce)

        h = hashlib.sha256()
        h.update(hash_string)
        return h.digest()

    def has_valid_hash_value(self):
        """ Checks if hash value produces enough 0's according to the difficulty level.

        :return bool: if difficulty level is met with the current nonce. If nonce is not set returns False
        """

        if self.nonce is None:
            return False

        hash_val_digest = self.get_hash_value()
        # print "Hash value digest:" + hash_val_digest
        binary_hash = ProofOfWork.binary_from_digest(hash_val_digest)
        valid_hash = ProofOfWork.check_if_enough_zeros(binary_hash, self.hash_difficulty_value)
        return valid_hash

    def get_counter(self):
        return self.counter

    def get_previous_block_hash(self):
        return self.previous_block_hash

    def get_data(self):
        return self.data
