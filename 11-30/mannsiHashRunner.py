import hashlib
import time

number_of_runs = 10000000

h = hashlib.sha256()

h.update("The initial seed")

start_time = time.time()

for i in range(0, number_of_runs):
    val = h.digest()
    h.update(val)


end_time = time.time()
duration = end_time - start_time
average_hash_time = duration/number_of_runs

print "Runtime of all hashes is '%s'" % duration
print "Average hashing runtime: '%s' seconds" % average_hash_time