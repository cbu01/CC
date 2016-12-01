""" Benchmarks the speed of the hashing algorithm """

import PowHelper
from timeit import default_timer as timer

start = timer()

s = PowHelper.generate_random_bit_string(128)
n = 15

x, x_int = PowHelper.find_x(s,n)
end = timer()
run_time = end-start
print "Time of run: {0} sec. Average time of hash is '{1}' sec. X found was '{2}'".format(run_time, run_time/x_int , x_int)

x_verified = PowHelper.verify_hash(s,x,n)

if x_verified:
    print "Hash is verified"
else:
    print "Hash NOT verified"
