""" Benchmarks the speed of the hashing algorithm """

import PowHelper
from timeit import default_timer as timer

start = timer()

s = "to_be_or_not_be_"
n = 15

x, x_int = PowHelper.find_x_competition(s,n)
end = timer()
run_time = end-start
print "Time of run: {0} sec. Average time of hash is '{1}' sec. X found was '{2}'".format(run_time, run_time/x_int , x_int)
