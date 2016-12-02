import random
import hashlib
import binascii


CMD_TASK_SUCCESS_REPLY = "CMD_TASK_SUCCESS_REPLY"
CMD_TASK_SUCCESS_REQUEST = "CMD_TASK_SUCCESS_REQUEST"
CMD_SEND_TASK_TO_WORKER = "CMD_SEND_TASK_TO_WORKER"
CMD_RECEIVE_WORK_FROM_WORKER = "CMD_RECEIVE_WORK_FROM_WORKER"


def generate_random_bit_string(size):
    return ''.join([str(random.randint(0,1)) for x in range(size)])


def find_x(s, n, printx=False):
    """ Finds an x such that the Sha256(s + x) has n number of last digits as 0 """
    x_counter = 1
    s_in_ascii = binary_to_ascii(s)
    while True:
        if printx:
            print "X counter: '%s'" % x_counter
        x = _binary_string_from_int(x_counter)

        enough_zeros = verify_hash(s_in_ascii, x, n)
        if enough_zeros:
            return x, x_counter

        x_counter += 1

def verify_hash(s_ascii, x_bin_string, n):
    """ Verifies that the hash of s+x has n trailing zeros in binary """

    h = hashlib.sha256()

    x_in_ascii = binary_to_ascii(x_bin_string)
    h.update(s_ascii + x_in_ascii)
    digest = h.digest()
    binary_val = _binary_from_digest(digest)
    enough_zeros = _check_if_enough_zeros(binary_val, n)
    return enough_zeros


def _check_if_enough_zeros(binary_val, n):
    substring = binary_val[-n:]
    if "1" in substring:
        return False
    else:
        return True


def _binary_string_from_int(int_val):
    """Returns a 128 bit long binary string"""
    x_bin_string = bin(int_val)[2:]
    x = (128 - len(x_bin_string)) * "0" + x_bin_string
    return x


def _binary_from_digest(digest):
    return bin(int(binascii.hexlify(digest), 16))


def binary_to_ascii(input, length=8):
    input_l = [input[i:i+length] for i in range(0,len(input),length)]
    return ''.join([chr(int(c,base=2)) for c in input_l])