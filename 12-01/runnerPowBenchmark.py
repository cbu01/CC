""" Benchmarks the speed of the hashing algorithm """

import sys

import PowHelper
from timeit import default_timer as timer

def run(s, n):

    start = timer()

    x, x_int = PowHelper.find_x_competition(s,n)
    end = timer()
    run_time = end-start
    print "Time of run: {0} sec. Average time of hash is '{1}' sec. The int value of X found was '{2}'".format(run_time, run_time/x_int , x_int)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "Usage: python runnerPowBenchmark.py 16CharLongString levelAsInValue"
        sys.exit()

    s = sys.argv[1]
    if len(s) != 16:
        print "ERROR: The input string s has to have length equal to 16"
        sys.exit()
    try:
        n = int(sys.argv[2])
    except:
        print "ERROR: Unable to cast level to int ..."
        sys.exit()
    run(s,n)