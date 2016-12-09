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