import hashlib
import time
import binascii


def hash_runtime_checker():
    number_of_runs = 10000000

    h = hashlib.sha256()

    h.update("The initial seed")

    start_time = time.time()

    for i in range(0, number_of_runs):
        val = h.digest()
        h.update(val)

    end_time = time.time()
    duration = end_time - start_time
    average_hash_time = duration / number_of_runs

    print "Runtime of all hashes is '%s'" % duration
    print "Average hashing runtime: '%s' seconds" % average_hash_time


def find_x(s, n):
    """ Finds an x such that the Sha256(s + x) has n number of last digits as 0 """
    x_counter = 1
    while True:
        print "X counter: '%s'" % x_counter

        h = hashlib.sha256()
        x = binary_string_from_int(x_counter)
        s_in_ascii = string_decode(s)
        x_in_ascii = string_decode(x)

        len_s = len(s_in_ascii)
        len_x = len(x_in_ascii)
        h.update(s_in_ascii + x_in_ascii)
        digest = h.digest()
        len_digest = len(digest)
        binary_val = binary_from_digest(digest)
        len_binary = len(binary_val)
        enough_zeros = check_if_enough_zeros(binary_val, n)

        if enough_zeros:
            return x

        x_counter += 1


def check_if_enough_zeros(binary_val, n):
    substring = binary_val[-n:]
    if "1" in substring:
        return False
    else:
        return True


def binary_string_from_int(int_val):
    """Returns a 128 bit long binary string"""
    x_bin_string = bin(int_val)[2:]
    x = (128 - len(x_bin_string)) * "0" + x_bin_string
    return x


def binary_from_digest(digest):
    return bin(int(binascii.hexlify(digest), 16))


def string_decode(input, length=8):
    input_l = [input[i:i+length] for i in range(0,len(input),length)]
    return ''.join([chr(int(c,base=2)) for c in input_l])


if __name__ == "__main__":
    s = bin(int(binascii.hexlify("Super long string that will generate many bits :)"), 16))[2:128]
    n = 20

    find_x(s, n)
