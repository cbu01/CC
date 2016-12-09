from BlockChain import BlockChain
import RSAWrapper
import Common

block_chain_name = "stupid_block_chain"

genesis_key = RSAWrapper.keygen()
client_keys = [RSAWrapper.keygen()]
client_ids = [Common.client_id_from_public_key(client_keys[0].publickey())]
client_amounts = [10]

bc = BlockChain(block_chain_name,
                genesis_key,
                client_ids,
                client_keys,
                client_amounts)


# TODO try adding a fake transaction to the bc
# TODO run the verify the bc audit function