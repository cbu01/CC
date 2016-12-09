import binascii
import uuid


def binary_from_digest(digest):
    return bin(int(binascii.hexlify(digest), 16))


def check_if_enough_zeros(binary_val, n):
    substring = binary_val[-n:]
    if "1" in substring:
        return False
    else:
        return True


def try_to_set_correct_nonce(block):
    nonce = uuid.uuid4().hex
    block.set_nonce(nonce)
    if block.has_valid_hash_value():
        return True
    return False


def verify_next_block_in_chain(next_block, block_chain):
    block_hash_internal_verification = next_block.has_valid_hash_value()
    if not block_hash_internal_verification:
        print "Block does not verify internal hash"
        return False

    current_latest_block = block_chain.get_latest_block()
    previous_block_hash_val = next_block.get_previous_block_hash()
    current_block_hash_val = current_latest_block.get_hash_value()

    if previous_block_hash_val != current_block_hash_val:
        print "Hash pointer of new block does not match hash value of previous block"
        return False

    return True