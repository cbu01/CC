from BlockChain import BlockChain
import RSAWrapper
import Common


def sanity_test():
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

    verifies = bc.audit()
    if not verifies:
        raise Exception("Empty BC does not verify")

    # Add transactions from account with 10 to a new account
    new_client_key = RSAWrapper.keygen()
    client_keys.append(new_client_key)
    client_public_keys = [key.publickey() for key in client_keys]
    client_ids.append(Common.client_id_from_public_key(new_client_key.publickey()))
    num_clients = len(client_ids)

    signature_message_text = Common.transaction_signature_text(num_clients, client_ids, [10, 0], [5, 5])
    signatures = [RSAWrapper.sign(signature_message_text, key) for key in client_keys]

    new_block = bc.create_block(num_clients, client_ids, client_public_keys, [-5, 5], signatures)
    block_added = bc.add_block(new_block)
    if not block_added:
        raise Exception("Unable to add new block")

    verifies = bc.audit()
    if not verifies:
        raise Exception("Could not verify block chain after adding transaction")

    print "== Successfully ran sanity_test()"


def withdraw_without_funds_test():
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

    verifies = bc.audit()
    if not verifies:
        raise Exception("Empty BC does not verify")

    # Try to subtract 15 from an account that only has 10
    new_client_key = RSAWrapper.keygen()
    client_keys.append(new_client_key)
    client_public_keys = [key.publickey() for key in client_keys]
    client_ids.append(Common.client_id_from_public_key(new_client_key.publickey()))
    num_clients = len(client_ids)

    signature_message_text = Common.transaction_signature_text(num_clients, client_ids, [10, 0], [-5, 15])
    signatures = [RSAWrapper.sign(signature_message_text, key) for key in client_keys]

    new_block = bc.create_block(num_clients, client_ids, client_public_keys, [-15, 15], signatures)
    if new_block:
        raise Exception("New block should not be created since there are not enough funds on the account")

    print "== Successfully ran widthdraw_without_funds_test()"


def illegal_signatures_test():
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

    verifies = bc.audit()
    if not verifies:
        raise Exception("Empty BC does not verify")

    # Add transactions from account with 10 to a new account
    new_client_key = RSAWrapper.keygen()
    client_keys.append(new_client_key)
    client_public_keys = [key.publickey() for key in client_keys]
    client_ids.append(Common.client_id_from_public_key(new_client_key.publickey()))
    num_clients = len(client_ids)

    signature_message_text = "Just some incorrect bullshit"
    signatures = [RSAWrapper.sign(signature_message_text, key) for key in client_keys]

    new_block = bc.create_block(num_clients, client_ids, client_public_keys, [-5, 5], signatures)
    if new_block:
        raise Exception("New block should not be created since signatures don't match")

    print "== Successfully ran illegal_signatures_test()"

if __name__ == "__main__":
    sanity_test()
    withdraw_without_funds_test()
    illegal_signatures_test()


