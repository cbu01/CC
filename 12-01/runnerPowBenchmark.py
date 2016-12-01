""" Benchmarks the speed of the hashing algorithm """

import PowHelper
from timeit import default_timer as timer
import binascii

start = timer()

# s = PowHelper.generate_random_bit_string(128)
s = bin(int(binascii.hexlify("Super long string that will generate many bits :)"), 16))[2:130]
n = 20

x, x_int = PowHelper.find_x(s,n)
end = timer()
run_time = end-start
print "Time of run: {0} sec. Average time of hash is '{1}' sec. X found was '{2}'".format(run_time, run_time/x_int , x_int)

start = timer()
x_verified = PowHelper.verify_hash(s,x,n)
end = timer()
run_time = end-start


print "Single hash run took '{0}'".format(run_time)
if x_verified:
    print "Hash is verified"
else:
    print "Hash NOT verified"
