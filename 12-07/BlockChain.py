import pickle
from Block import Block
import Common
import RSAWrapper


class BlockChain:
    def __init__(self,
                 block_chain_file_name,
                 genesis_key,
                 initial_client_ids,
                 initial_client_keys,
                 initial_client_amounts,
                 genesis_init_balance=1000000,
                 load_blockchain_from_file=True):

        self.genesis_hash_pointer = "17"
        self.genesis_init_balance = genesis_init_balance
        self.initial_client_amounts = initial_client_amounts
        self.initial_client_keys = initial_client_keys
        self.initial_client_ids = initial_client_ids
        self.genesis_key = genesis_key
        if genesis_key is not None:
            self.genesis_client_id = Common.client_id_from_public_key(self.genesis_key.publickey())
        self.block_chain_file_name = block_chain_file_name
        self.latest_block = None
        self.blocks_dictionary = {}  # {blockHashId: block}
        if load_blockchain_from_file:
            loaded = self._load_block_chain_from_file()
            if not loaded:
                self.first_block_chain_initialization()

    def _save_block_chain_to_file(self):
        pickle.dump((self.blocks_dictionary, self.latest_block, self.genesis_client_id, self.genesis_init_balance),
                    open(self.block_chain_file_name, "wb"))

    def _load_block_chain_from_file(self):
        try:
            self.latest_block, self.genesis_client_id, self.genesis_init_balance = pickle.load(
                open(self.block_chain_file_name, "rb"))
            return True
        except:
            return False

    @staticmethod
    def load_from_file(block_chain_file_name):
        # This function is used by clients to load the bc
        blocks_dict, latest_block, genesis_client_id, genesis_init_balance = pickle.load(
            open(block_chain_file_name, "rb"))
        block_chain = BlockChain(block_chain_file_name, None, [], [], [], genesis_init_balance, False)
        block_chain.blocks_dictionary = blocks_dict
        block_chain.latest_block = latest_block
        block_chain.genesis_client_id = genesis_client_id
        return block_chain

    def first_block_chain_initialization(self):
        genesis_block = Block(
            1,
            [self.genesis_client_id],
            [self.genesis_key.publickey()],
            [0],
            [self.genesis_init_balance],
            ["Incorrect genesis signature"],
            self.genesis_hash_pointer)
        self.blocks_dictionary[genesis_block.hash_value()] = genesis_block
        self.latest_block = genesis_block

        # Now we add the first block that spreads the first genesis money
        client_ids = []
        client_ids.extend(self.initial_client_ids)
        client_ids.insert(0, self.genesis_client_id)
        num_clients = len(client_ids)

        client_keys = [self.genesis_key]
        client_keys.extend(self.initial_client_keys)

        client_public_keys = [x.publickey() for x in client_keys]

        start_balances = [self.genesis_init_balance]
        start_balances.extend([0 for x in client_ids[1:]])
        genesis_end_balance = self.genesis_init_balance - sum(self.initial_client_amounts)
        end_balances = [genesis_end_balance]
        end_balances.extend(self.initial_client_amounts)

        signature_message_text = Common.transaction_signature_text(num_clients, client_ids, start_balances,
                                                                   end_balances)
        signatures = [RSAWrapper.sign(signature_message_text, key) for key in client_keys]

        amount_changes_list = [genesis_end_balance - self.genesis_init_balance]
        amount_changes_list.extend(self.initial_client_amounts)

        initial_genesis_transfer_block = self.create_block(num_clients, client_ids, client_public_keys,
                                                           amount_changes_list, signatures)
        success = self.add_block(initial_genesis_transfer_block)
        if success:
            print "Managed to create the first couple of blocks"
            self._save_block_chain_to_file()
        else:
            print "Could not create the initial genesis transfer block"

    def _get_last_end_amount_for_client(self, client_id):
        curr_block = self.latest_block
        while True:
            current_block_has_client = client_id in curr_block.list_of_client_ids
            if current_block_has_client:
                client_index = curr_block.get_client_ids().index(client_id)
                client_latest_ending_balance = curr_block.get_client_ending_amounts()[client_index]
                return client_latest_ending_balance

            # Check if this is the genesis block. Then we don't continue
            is_genesis_block = curr_block.get_previous_block_hash() == self.genesis_hash_pointer
            if is_genesis_block:
                break

            hash_pointer_to_prev_block = curr_block.get_previous_block_hash()
            if hash_pointer_to_prev_block not in self.blocks_dictionary:
                message = "Did not find hash pointer value of previous transaction in dictionary"
                print message
                raise Exception(message)

            curr_block = self.blocks_dictionary[hash_pointer_to_prev_block]

        # Got here means this is clients first transaction
        return 0

    def add_block(self, block):
        if not block.verify_block():
            print "Block not verified"
            return False

        block_hash_pointer_val = block.get_previous_block_hash()
        latest_block_hash = self.latest_block.hash_value()
        if block_hash_pointer_val != latest_block_hash:
            print "Hash pointer of new block does not match hash value of latest block"
            return False

        block_own_hash_value = block.hash_value()
        if block_own_hash_value in self.blocks_dictionary:
            print "Block has already been added to block chain"
            return False

        self.blocks_dictionary[block_own_hash_value] = block
        self.latest_block = block
        self._save_block_chain_to_file()
        return True

    def create_block(self,
                     num_clients,
                     list_of_client_ids,
                     list_client_public_keys,
                     list_of_amount_changes,
                     list_of_signatures):
        previous_block_hash = self.latest_block.hash_value()

        client_start_balances = []
        client_end_balances = []

        for i in range(len(list_client_public_keys)):
            client_id = list_of_client_ids[i]
            client_amount_change = list_of_amount_changes[i]
            client_start_balance = self._get_last_end_amount_for_client(client_id)
            client_start_balances.append(client_start_balance)
            has_enough_balance = client_start_balance > -client_amount_change
            if not has_enough_balance:
                print "Client with ID {0} only has a balance {1} but is trying to subtract {2}".format(client_id,
                                                                                                       client_start_balance,
                                                                                                       client_amount_change)
                return False
            client_end_balance = client_start_balance + client_amount_change
            client_end_balances.append(client_end_balance)

        block = Block(num_clients,
                      list_of_client_ids,
                      list_client_public_keys,
                      client_start_balances,
                      client_end_balances,
                      list_of_signatures,
                      previous_block_hash)

        block_verified = block.verify_block()
        if not block_verified:
            print "Block not verified"
            return False

        return block

    def audit(self):
        bcv = BlockChainVerifier()
        verified = bcv.verify_entire_block_chain(self.latest_block, self.blocks_dictionary, self.genesis_hash_pointer)
        if not verified:
            print "Block chain was not verified !"

        return verified


class BlockChainVerifier:
    def __init__(self, ):
        # dict that stores latest known info of the start balances of each account by account id
        self.current_start_balances_of_accounts = {}

    def verify_entire_block_chain(self, latest_block, blocks_dictionary, genesis_hash_pointer):
        current_block = latest_block

        while current_block.get_previous_block_hash() != genesis_hash_pointer:
            if not current_block.verify_block():
                print "Block does not verify internally"
                return False

            # Store starting balances of current block
            client_ids_starting_balance_ending_balance = current_block.get_client_ids_starting_balance_ending_balance()
            client_ids_and_starting_balance = [(x[0], x[1]) for x in client_ids_starting_balance_ending_balance]
            self._update_last_known_starting_balances(client_ids_and_starting_balance)

            # Access previous block and compare end with dict
            previous_block = blocks_dictionary[current_block.get_previous_block_hash()]
            client_ids_starting_balance_ending_balance = previous_block.get_client_ids_starting_balance_ending_balance()
            client_ids_and_ending_balance = [(x[0], x[2]) for x in client_ids_starting_balance_ending_balance]
            previous_balances_check_out = self._check_previous_starting_balances(client_ids_and_ending_balance)
            if not previous_balances_check_out:
                print "Accounts do not add up. Some account does not have a correct balance"
                return False

            current_block = previous_block

        return True

    def _update_last_known_starting_balances(self, client_ids_and_starting_balance):
        """ Updates the list of the latest known starting balances of client accounts.

        Args:
            client_ids_and_starting_balance (list(tuple)): a list of tuples. Each tuple is (client_id, starting_balance)
        """
        for client_id, starting_balance in client_ids_and_starting_balance:
            self.current_start_balances_of_accounts[client_id] = starting_balance

    def _check_previous_starting_balances(self, client_ids_and_ending_balance):
        """ Checks if the ending balance of each given account id matches the previous known starting balance
            This should be the case that an ending balance should always match the latest known starting balance for an account

        Args:
            client_ids_and_ending_balance (list(tuple)): a list of tuples. Each tuple is (client_id, ending_balance)

        Returns:
            bool: True if all accounts have the same ending balance as last previous starting balance (or if there is
                  no known previous starting balance. False otherwise.
        """
        float_threshold = 0.0001

        for client_id, ending_balance in client_ids_and_ending_balance:
            if client_id in self.current_start_balances_of_accounts:
                last_known_starting_balance = self.current_start_balances_of_accounts[client_id]
                if abs(last_known_starting_balance - ending_balance) > float_threshold:
                    print "Account with ID {0} does not have matching start and end balances. " \
                          "The start balance is {1} while the previously known end balance is {2}".format(client_id,
                                                                                                          last_known_starting_balance,
                                                                                                          ending_balance)

        return True
