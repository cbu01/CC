from Crypto.Random import random
import gmpy2
import binascii

p = 251 # prime

def get_shares(secret, n, k):
    
    # generate k empty strings (the will be filled with the secrets later)
    result_list = []
    for i in range(n):
        result_list.append("")
        
    # generate random coefficients
    coeff = []
    for a in range(k-1): 
        trying = True
        while trying:
            r = random.getrandbits(8) # returns long
            r_int = int(r)
            if r_int < p:
                trying = False
                coeff.append(r_int) 
    print "coeffs " + str(coeff)
    
    # turn to bin and add leading zeros to fill up whole bytes
    binary_secret = __turnToBin(str(secret))
    print "binary_secret " + str(binary_secret)
    
    # iterate over the message
    while len(binary_secret) > 0:
        
        # take the first byte
        current_byte  = binary_secret[0:8]
        binary_secret = binary_secret[8:]
        print "current byte " + str(__turnBinToInt(current_byte))
        print "binary secret " + str(binary_secret)
        # convert to int
        current_int = __turnBinToInt(current_byte)     
                       
        # calculate q(i) for i in n
        for i in range(1,n+1):
            sum = current_int
            for j in range(k-1):
                sum += i * coeff[j]**(j+1)
            hex_sum = hex(int(sum % p))[2:]
            print "result_list?? " + str(hex_sum)
            result_list[(i-1) % n] = result_list[(i-1) % n] + str(hex_sum)
    result = []
    print "result_list " + str(result_list)
    for i in range(n):
        result.append((i+1,result_list[i]))        
    return result

def combine(k,n,p,subsecrets):
    
    randsubsecrets = []
    # randomly choose k subsecrets
    for i in range(k):
        s = random.choice(subsecrets)
        randsubsecrets.append(s)
        subsecrets.remove(s)
        
    # convert hex secret to integer list
    int_secrets = []
    for r in randsubsecrets:
        print "current secret " + str(r)
        c = []
        hex_list = r[1]
        while len(hex_list) > 0:
            h = hex_list[:2] # get first two numbers from hex_list
            hex_list = hex_list[2:] # remove first two numbers from hex_list 
            int_value = int(h,16) # convert to integer
            c.append(int_value)
        int_secrets.append((r[0],c)) # collect index and list of integers
    print "int secrets: " + str(int_secrets)
    
    # get secret length as stopper for the loop
    length = len(int_secrets[0][1])   # get number of integers
      
    sum_collector = ""   
         
    for z in range(length): # for each integer/block (represents a char)    
        
        # calculate result for each block
        sum = 0
        for j in range(k):
            dividend = 1
            divisor = 1
            for l in range(k):
                if j != l:
                    dividend = dividend * int_secrets[l][0]
                    divisor = divisor * (int_secrets[l][0]-int_secrets[j][0]) 
            dividend = (int_secrets[j][1][z] * dividend) % p
            divisor = gmpy2.invert((divisor % p), p)   
            sum = (sum + ((dividend * divisor) % p)) % p
            print "sum " + str(sum)
        # save encrypted char to list
        print "sum in z loop " + str(sum)
        sum_collector = sum_collector + chr(sum % p)
    return sum_collector

            
# convert a string into its binary representation
# @string: ascii string to convert
# @return: binary representation of the string 
def __turnToBin(string):
    b = bin(int(binascii.hexlify(string), 16))[2:]
    # add leading zeros
    x = 8 - (len(b) % 8)
    while x > 0:
        b = '0' + b
        x -= 1
    return b 
 
def __turnBinToInt(b):
    return int(b,2)

def __turnIntToHex(b):
    return hex(int) 
 
# turn a string from binary representation into a string of ascii characters
# @b string in binary representation
# @return: ascii string
def __turnBinToString(b):
    s = binascii.unhexlify('%x' % int(b,2))
    return s 
 
if __name__ == "__main__":
    secret = "blah"
    print "Secret to hide: " + str(secret)
    subsecrets = get_shares(secret, 6, 3)   
    print "The secret is divided into the following shares: "+ str(subsecrets) 
    joinedsecret = combine(3,6,p,subsecrets)
    print "Restored secret: " + str(joinedsecret)