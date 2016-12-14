from BlockChain import BlockChain
from Block import Block
import time
import ProofOfWork


def run_sanity_test():
    hash_difficulty_value = 15

    bc = BlockChain()

    for i in range(10):
        prev_block = bc.get_target_block()
        timestamp = int(time.time())
        data = str(timestamp)
        new_counter = prev_block.get_counter() + 1

        block = Block(prev_block.get_hash_value(),
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
    while True:
        nonce_found = ProofOfWork.try_to_set_correct_nonce(block)
        if nonce_found:
            return


def run_illegal_hash_value_block_test():
    hash_difficulty_value = 15
    bc = BlockChain()

    prev_block = bc.get_target_block()
    timestamp = int(time.time())
    data = str(timestamp)
    new_counter = prev_block.get_counter() + 1

    wrong_hash_value = "asdasdfasdfasdf"

    block = Block(wrong_hash_value, # prev_block.get_hash_value(),
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

    prev_block = bc.get_target_block()
    timestamp = int(time.time())
    data = str(timestamp)
    new_counter = prev_block.get_counter() + 1

    block = Block(prev_block.get_hash_value(),
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


def run_copy_block_chain_test():
    hash_difficulty_value = 15

    bc1 = BlockChain()
    bc2 = BlockChain()

    # Add 10 blocks to bc1 and 5 blocks to bc2
    for i in range(10):
        prev_block = bc1.get_target_block()
        timestamp = int(time.time())
        data = str(timestamp)
        new_counter = prev_block.get_counter() + 1

        block = Block(prev_block.get_hash_value(),
                      timestamp,
                      data,
                      new_counter,
                      hash_difficulty_value)

        set_nonce(block)
        success = bc1.add_block(block)
        if i < 5:
            success = success and bc2.add_block(block)
        if not success:
            message = "Unable to add block"
            print message
            raise Exception(message)

    # Copy blocks from bc1 to bc2
    last_safe_hash_from_bc2 = bc2.get_latest_safe_block_hash_id()
    blocks_to_copy = bc1.get_blocks_since_hash_id(last_safe_hash_from_bc2)
    bc2.add_blocks_from_another_chain(blocks_to_copy)
    if bc2.get_number_of_blocks() != 11:  # 10 + genesis block
        message = "Blocks in bc2 should be 11  but instead were only " + str(bc2.get_number_of_blocks())
        print message
        raise Exception(message)

    print "== Successfully ran the run_copy_block_chain_test"


def run_copy_block_chain_from_genesis_test():
    hash_difficulty_value = 15

    bc1 = BlockChain()
    bc2 = BlockChain()

    # Add 10 blocks to bc1 and 5 blocks to bc2
    for i in range(1):
        prev_block = bc1.get_target_block()
        timestamp = int(time.time())
        data = str(timestamp)
        new_counter = prev_block.get_counter() + 1

        block = Block(prev_block.get_hash_value(),
                      timestamp,
                      data,
                      new_counter,
                      hash_difficulty_value)

        set_nonce(block)
        success = bc1.add_block(block)
        if not success:
            message = "Unable to add block"
            print message
            raise Exception(message)

    # Copy block from bc1 to bc2
    last_safe_hash_from_bc2 = bc2.get_latest_safe_block_hash_id()
    blocks_to_copy = bc1.get_blocks_since_hash_id(last_safe_hash_from_bc2)
    bc2.add_blocks_from_another_chain(blocks_to_copy)
    if bc2.get_number_of_blocks() != 2:  # 1 + genesis block
        message = "Blocks in bc2 should be 2  but instead were only " + str(bc2.get_number_of_blocks())
        print message
        raise Exception(message)

    print "== Successfully ran the run_copy_block_chain_from_genesis_test"



if __name__ == "__main__":
    run_sanity_test()
    run_illegal_hash_value_block_test()
    run_illegal_nonce_block_test()
    run_copy_block_chain_test()
    run_copy_block_chain_from_genesis_test()
