from Crypto.Random import random
import gmpy2
import binascii 

""" Divides a secret into n blocks. k blocks should be enough to restore 
the secret 
@secret: the secret, that should be shared
@n: number of blocks into which the secret should be divided
@k: number of blocks required to determine the secret
@p: prime 
@return: tuple(n, k, p, list of resulting blocks) """
def get_shares(secret, n, k, p=251):
    
    # check size of p
    # depending on which ascii symbols should remain usable, this should not be 
    # too small either...
    # check, that p is not larger than 251, because this would cause trouble
    if (p > 251):
        print "Please choose a prime which is smaller or equal to 251."
    
    # generate k empty strings (the will be filled with the secrets later)
    result_list = []
    for i in range(n):
        result_list.append("")
    
    # turn message into binary format and add leading zeros to fill up whole bytes
    binary_secret = __turnToBin(str(secret))
    
    # iterate over the message byte by byte and generate 6 secrets for each byte
    while len(binary_secret) > 0:
             
        # generate k-1 random coefficients
        coeff = []
        for a in range(k-1):
            # choose a random coefficient
            r = random.getrandbits(8) # returns an 8 byte value (long)
            r_int = int(r) # convert to int
            r_int = r_int % p # ensure that int_r is not larger than p
            coeff.append(r_int) 
        
        # take the first byte and convert it to integer value
        # remove the first byte from the string
        current_byte  = binary_secret[0:8]
        binary_secret = binary_secret[8:]
        current_int = __turnBinToInt(current_byte)     
                       
        # calculate q(i) for i in n
        for i in range(1,n+1):
            sum = current_int
            # calculate elements for addition
            for j in range(k-1):
                # a*(x^k)
                sum += coeff[j]*(i**(j+1))
            # convert to hex representation
            hex_sum = hex(int(sum % p))[2:]
            # ensure that hex value has the right length 
            # Eg. hex(1)[2:] returns '1' and not '01' as desired
            if len(hex_sum) < 2:
                hex_sum = '0'+hex_sum
     
            # collect all results in a list
            result_list[(i-1) % n] = result_list[(i-1) % n] + str(hex_sum)
    
    # merge the results of each byte for each secretholder into a string
    result = []
    for i in range(n):
        result.append((i+1,result_list[i]))        
    return (n,k,p,result)


""" Combines the blocks of the shared secret to determine the original secret
@n: number of blocks, into which the original secret was split into
@k: number of blocks to determine the original secret
@p: prime
@sharedsecrets: list of blocks, into which the secret was split
@return: cleartext """
def combine(sharedsecrets, n, k, p=251):
    
    # randomly choose k sharedsecrets
    randsecrets = []
    for i in range(k):
        s = random.choice(sharedsecrets)
        randsecrets.append(s)
        sharedsecrets.remove(s)
        
    # convert hex secret of each randomly chosen sharedsecret into an integer list
    int_secrets = []
    for r in randsecrets: # for each k
        c = []
        hex_list = r[1]
        while len(hex_list) > 0: # as long as there are still hex values to convert
            h = hex_list[:2] # get first two numbers from hex_list
            hex_list = hex_list[2:] # remove first two numbers from hex_list 
            int_value = int(h,16) # convert to integer
            c.append(int_value) 
        int_secrets.append((r[0],c)) # collect index and list of integers
    
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
                    dividend = dividend * int_secrets[l][0] % p
                    divisor = divisor * ((int_secrets[l][0]-int_secrets[j][0]) % p) % p
            dividend = (int_secrets[j][1][z] * dividend) % p
            divisor = gmpy2.invert((divisor % p), p)   
            sum = (sum + ((dividend * divisor) % p)) % p
        # save encrypted char to list
        sum_collector = sum_collector + chr(sum % p)
    return sum_collector

def prettyprint(output_of_get_shares):
    n = output_of_get_shares[0]
    k = output_of_get_shares[1]
    p = output_of_get_shares[2]
    shares = output_of_get_shares[3]
    for i in range(len(shares)):
        print " "
        print "n = "+str(n)+", k = "+str(k)+", p = "+str(p)+", j = "+str(i)+","
        print "secret: " + str(shares[i][1]) 
        print " "    
    print " " 
            
""" convert a string into its binary representation
    @string: ascii string to convert
    @return: binary representation of the string """
def __turnToBin(string):
    b = bin(int(binascii.hexlify(string), 16))[2:]
    # add leading zeros
    x = 8 - (len(b) % 8)
    while x > 0:
        b = '0' + b
        x -= 1
    return b 

""" turn binary string to int
@b: binary string
@return: int """ 
def __turnBinToInt(b):
    return int(b,2)

 
""" Test """ 
if __name__ == "__main__":
    
    # set parameters
    n = 6
    k = 3
    secret = "This is a big secret. Don't tell anyone!!!"
    print "Secret to hide: " + str(secret)
    
    # encrypt
    sharedsecrets = get_shares(secret, n, k)  
    print "The secret is divided into the following shares: "+ str(sharedsecrets) 

    # print out the results with the pretty printer
    print "Pretty Printer: "
    prettyprint(sharedsecrets)

    # recover
    joinedsecret = combine(sharedsecrets[3], n, k)
    print "Restored secret: " + str(joinedsecret)