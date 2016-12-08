import pickle
from Block import Block


class BlockChain:
    def __init__(self, block_chain_file_name):
        self.block_chain_file_name = block_chain_file_name
        self.latest_block = None

    def _save_block_chain_to_file(self):
        pickle.dump(self.latest_block, open(self.block_chain_file_name, "wb"))

    def _load_block_chain_from_file(self):
        self.latest_block = pickle.load(open(self.block_chain_file_name, "rb"))

    @staticmethod
    def first_block_chain_initialization(block_file_name, genesis_key, list_of_ids_to_split_genesis_dollars):
        # TODO create the genesis block
        genesis_block = Block("I think it's ok that this is nonsense", None, "GENESIS_BLOCK_HASH")

        # TODO create the initial transfer block from the genesis block
        pass

    def add_block(self, message, signatures):
        # TODO create block object
        # TODO map what I want the block to actually get
        new_block = None
        new_block_verified = new_block.verify_block()
        if new_block_verified:
            print "New block successfully verified and added"
            self.latest_block = new_block
            self._save_block_chain_to_file()
            return True
        else:
            print "Unable to verify new block"
            return False

    def verify_block_chain(self):
        bcv = BlockChainVerifier()
        verified = bcv.verify_entire_block_chain(self.latest_block)
        if not verified:
            print "Block chain was not verified !"

        return verified


class BlockChainVerifier:
    def __init__(self):
        # dict that stores latest known info of the start balances of each account by account id
        self.current_start_balances_of_accounts = {}

    def verify_entire_block_chain(self, latest_block):
        current_block = latest_block

        while current_block.previous_block is not None:
            if not current_block.verify_block():
                print "Block does not verify internally"
                return False

            # Store starting balances of current block
            client_ids_starting_balance_ending_balance = current_block.get_client_ids_starting_balance_ending_balance()
            client_ids_and_starting_balance = [(x[0], x[1]) for x in client_ids_starting_balance_ending_balance]
            self._update_last_known_starting_balances(client_ids_and_starting_balance)

            # Access previous block and compare O with dict
            client_ids_starting_balance_ending_balance = current_block.previous_block.get_client_ids_starting_balance_ending_balance()
            client_ids_and_ending_balance = [(x[0], x[2]) for x in client_ids_starting_balance_ending_balance]
            previous_balances_check_out = self._check_previous_starting_balances(client_ids_and_ending_balance)
            if not previous_balances_check_out:
                print "Accounts do not add up. Some account does not have a correct balance"
                return False

            current_block = current_block.previous_block

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
                          "The start balance is {1} while the previously known end balance is {2}".format(client_id, last_known_starting_balance, ending_balance)

        return True


