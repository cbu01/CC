import binascii


def binary_from_digest(digest):
    return bin(int(binascii.hexlify(digest), 16))


def check_if_enough_zeros(binary_val, n):
    substring = binary_val[-n:]
    if "1" in substring:
        return False
    else:
        return True