import pickle
import os
import os.path
import time


class BigBrotherBank:
    def __init__(self, data_file_name):
        self._data_file_name = data_file_name
        self._balances_dict = {}
        self._transactions_dict = {}
        self._load_data_from_file()

    def pay(self, id1, id2, amount):
        """ Returns a transaction id if id1 can transfer amount to id2.
            Returns False otherwise or if something went wrong """
        if id1 not in self._balances_dict:
            # Id1 does not exist in system
            return False

        if id2 not in self._balances_dict:
            # Id2 does not exist in system
            return False

        id1_balance = self._balances_dict[id1]
        if id1_balance < amount:
            # Id1 does not have the funds to transfer the money
            return False

        # Update the amounts
        self._balances_dict[id1] -= amount
        self._balances_dict[id2] += amount

        # Save the transaction
        transaction_id = self._generate_new_id()
        self._transactions_dict[transaction_id] = ((id1, id2, amount, time.time()))

        return transaction_id

    def query(self, id1, id2, transaction_id, amount):
        """ Returns true if id1 has payed amount to id2 where the id of the transaction is transactionId """
        if transaction_id not in self._transactions_dict:
            # Transaction with this id does not exist
            return False

        # Check if every part of the query matches the saved transaction
        logged_id1, logged_id2, logged_amount = self._transactions_dict[transaction_id]
        if logged_id1 == id1 and logged_id2 == id2 and logged_amount == amount:
            return True

    def _load_data_from_file(self):
        if not self._data_file_exists():
            self._create_initial_data()
        else:
            self._balances_dict, self._transactions_dict = pickle.load(open(self._data_file_name, "rb"))

    def _save_data_to_file(self):
        data_to_save = self._balances_dict, self._transactions_dict
        pickle.dump(data_to_save, open(self._data_file_name, "wb"))

    def _data_file_exists(self):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, self._data_file_name)
        return os.path.isfile(file_path)

    def _create_initial_data(self):
        #TODO update the ids and maybe the values
        self._balances_dict = {"1": 10, "2": 10}

    def _generate_new_id(self):
        #TODO
        pass


if __name__ == "__main__":
    data_file = "Database.pickle"
    bbb = BigBrotherBank(data_file)
    # TODO start listening for incoming upd calls


