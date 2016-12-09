from BlockChain import BlockChain
from Block import Block
import time


def run_sanity_test():
    hash_difficulty_value = 15

    bc = BlockChain()

    for i in range(10):
        prev_block = bc.get_latest_block()
        timestamp = int(time.time())
        data = str(timestamp)
        new_counter = prev_block.get_counter() + 1

        block = Block(prev_block,
                      prev_block.get_hash_value(),
                      timestamp,
                      data,
                      new_counter,
                      hash_difficulty_value)

        set_nonce(block)
        success = bc.add_block(block)
        if not success:
            print "Unable to add block"
            raise Exception()

    success = bc.audit()
    if not success:
        print "Unable to audit the block chain"
        raise Exception

    print "== Successfully ran the simple sanity check test"


def set_nonce(block):
    nonce_counter = 1
    while True:
        nonce = str(nonce_counter)
        # print "Trying nonce " + nonce
        block.set_nonce(nonce)
        if block.has_valid_hash_value():
            return
        nonce_counter += 1


def run_illegal_hash_value_block_test():
    hash_difficulty_value = 15
    bc = BlockChain()

    prev_block = bc.get_latest_block()
    timestamp = int(time.time())
    data = str(timestamp)
    new_counter = prev_block.get_counter() + 1

    wrong_hash_value = "asdasdfasdfasdf"

    block = Block(prev_block,
                  wrong_hash_value, # prev_block.get_hash_value(),
                  timestamp,
                  data,
                  new_counter,
                  hash_difficulty_value)

    set_nonce(block)
    success = bc.add_block(block)
    if success:
        print "Should not have been able to add illegal block !!!"
        raise Exception()

    print "== Successfully ran the run_illegal_hash_value_block_test"


def run_illegal_nonce_block_test():
    hash_difficulty_value = 15
    bc = BlockChain()

    prev_block = bc.get_latest_block()
    timestamp = int(time.time())
    data = str(timestamp)
    new_counter = prev_block.get_counter() + 1

    block = Block(prev_block,
                  prev_block.get_hash_value(),
                  timestamp,
                  data,
                  new_counter,
                  hash_difficulty_value)

    # set_nonce(block)
    block.set_nonce("wrong nonce value")
    success = bc.add_block(block)
    if success:
        print "Should not have been able to add illegal block !!!"
        raise Exception()

    print "== Successfully ran the run_illegal_nonce_block_test"

if __name__ == "__main__":
    run_sanity_test()
    run_illegal_hash_value_block_test()
    run_illegal_nonce_block_test()