import hashlib
import time
import binascii

""" Calculate 10000000 hash values """
def hash_runtime_checker():
    number_of_runs = 10000000

    # init
    h = hashlib.sha256()
    h.update("The initial seed")

    # get start time
    start_time = time.time()

    # calculate number_of_runs hashes
    for i in range(0, number_of_runs):
        val = h.digest()
        h.update(val)

    # get end time
    end_time = time.time()
    
    # calculate elapsed time
    duration = end_time - start_time
    average_hash_time = duration / number_of_runs

    print "Runtime of all hashes is '%s'" % duration
    print "Average hashing runtime: '%s' seconds" % average_hash_time
    
    

""" Finds an x such that the Sha256(s + x) has n number of last digits as 0 
@s: prefix
@n: number of zeros
@return: suffix x"""
def find_x(s, n):
    
    # start timer
    start_time = time.time()
    
    x_counter = 1
    while True:

        h = hashlib.sha256()
        
        # create a binary string from counter (use that as suffix)
        x = binary_string_from_int(x_counter)
        # convert to ascii value
        s_in_ascii = string_decode(s)
        x_in_ascii = string_decode(x)
        # calculate SHA value
        h.update(s_in_ascii + x_in_ascii)
        digest = h.digest()
        # convert result into binary string
        binary_val = binary_from_digest(digest)
        # check if there are enough zeros
        enough_zeros = check_if_enough_zeros(binary_val, n)

        if enough_zeros:
            
            # stop time
            end_time = time.time()
            
            print "Found a hash value with enough zeros " + str(binary_val)
            print "suffix is: " + str(x)
            
            # calculate elapsed time
            duration = end_time - start_time
            average_hash_time = duration / x_counter

            print "Runtime of all hashes is '%s'" % duration
            print "Average hashing runtime: '%s' seconds" % average_hash_time
            
            return x

        x_counter += 1

""" check if the suffix contains enough zeros 
@binatry_val: string in binary representation
@n: number of zeros
@return: boolean value that indicates, if the suffix contains enough zeros. """
def check_if_enough_zeros(binary_val, n):
    substring = binary_val[-n:]
    if "1" in substring:
        return False
    else:
        return True


""" Converts integer value into a 128 bit long binary string
@int_val: integer value
@return: 128 bit long binary string """
def binary_string_from_int(int_val):
    x_bin_string = bin(int_val)[2:]
    # fill up the end of the string with zeros
    x = (128 - len(x_bin_string)) * "0" + x_bin_string
    return x

""" Converts ascii string into binary representation 
@digest: ascii string
@return: binary representation of the string"""
def binary_from_digest(digest):
    return bin(int(binascii.hexlify(digest), 16))

""" Converts a binary string to an ascii string
@input: binary string to convert
@length: length of blocks representing an ascii character (8 bit)
@return: ascii string """
def string_decode(input, length=8):
    # chunk input into a list of 8 bit sublists
    input_l = [input[i:i+length] for i in range(0,len(input),length)]
    # convert to string
    return ''.join([chr(int(c,base=2)) for c in input_l])

""" test """
if __name__ == "__main__":
    
    # check the has function
    s = bin(int(binascii.hexlify("Super long string that will generate many bits :)"), 16))[2:128]
    n = 25
    find_x(s, n)
    
    print " "
    
    # run the hash_runtime_checker
    hash_runtime_checker()
