import pickle
import socket
import os
import os.path
import time
import uuid
import Common
import RSAWrapper


class BigBrotherBank:
    def __init__(self, data_file_name):
        self._key = self._load_keys("BBBPrivateKey.pickle")
        self._client_public_keys = {}
        self._data_file_name = data_file_name
        self._balances_dict = {}
        self._transactions_dict = {}
        self._next_transaction_int_id = 100
        self._load_data_from_file()
        self._host = "localhost"
        self._port = 10555
       

        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._s.bind((self._host,self._port))

    def pay(self, id1, id2, amount):
        """ Returns a transaction id if id1 can transfer amount to id2.
            Returns False otherwise or if something went wrong """
        print "Got payment request from id1: {0}, id2:{1} and amount: {2}".format(id1, id2, amount)

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

        self._save_data_to_file()

        return transaction_id

    def query(self, id1, id2, transaction_id, amount):
        """ Returns true if id1 has payed amount to id2 where the id of the transaction is transactionId """
        print "Got query request from id1: {0}, id2:{1}, transactionId:{2} and amount: {3}".format(id1, id2, transaction_id, amount)
        if transaction_id not in self._transactions_dict:
            # Transaction with this id does not exist
            return False

        # Check if every part of the query matches the saved transaction
        logged_id1, logged_id2, logged_amount, time_stamp = self._transactions_dict[transaction_id]
        if logged_id1 == id1 and logged_id2 == id2 and logged_amount == float(amount):
            return True
        return False

    def register_client(self, client_id, client_public_key):
        if client_id in self._client_public_keys:
            # Client is already registered, not cool
            return False
        self._client_public_keys[client_id] = client_public_key
        self._save_data_to_file()
        return True

    def _load_data_from_file(self):
        if not self._data_file_exists(self._data_file_name):
            self._create_initial_data()
        else:
            self._balances_dict, self._transactions_dict, self._next_transaction_int_id, self._client_public_keys = pickle.load(open(self._data_file_name, "rb"))
            print "All current balances for accounts are :" + str(self._balances_dict)

    def _save_data_to_file(self):
        data_to_save = (self._balances_dict, self._transactions_dict, self._next_transaction_int_id, self._client_public_keys)
        pickle.dump(data_to_save, open(self._data_file_name, "wb"))

    def _data_file_exists(self, data_file_name):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, data_file_name)
        return os.path.isfile(file_path)

    def _create_initial_data(self):
        self._balances_dict = {Common.int_to_id(1): 10, Common.int_to_id(2): 10}
        self._save_data_to_file()

    def _generate_new_id(self):
        self._next_transaction_int_id += 1
        return Common.int_to_id(self._next_transaction_int_id)
        #return uuid.uuid4().hex

    def _load_keys(self, key_file_name):
        key_file_exists = self._data_file_exists(key_file_name)
        if not key_file_exists:
            _key = RSAWrapper.keygen()
            public_key = _key.publickey()
            pickle.dump(_key, open(key_file_name, "wb"))
            pickle.dump(public_key, open("BBBPublicKey.pickle", "wb"))
        else:
            _key = pickle.load(open(key_file_name, "rb"))

        return _key

    def Listen(self):
        while True:
            data, addr = self._s.recvfrom(2048)
            message = pickle.loads(data)
            if message[0] == "PAY" and len(message) == 4:
                try: 
                    a = message[3]
                    success = self.pay(message[1], message[2], message[3])
                    self._s.sendto(str(success), addr)
                except ValueError:
                    self._s.sendto(str(False), addr)
            elif message[0] == "QUERY" and len(message) == 5:
                try:
                    a = float(message[4])
                    success = self.query(message[1], message[2], message[3], message[4])
                    self._s.sendto(str(success), addr)
                except ValueError:
                    self._s.sendto(str(False), addr)
            elif message[0] == "REGISTER" and len(message) == 3:
                success = self.register_client(message[1], message[2])
                self._s.sendto(str(success), addr)
            else:
                self._s.sendto(str(False), addr)


if __name__ == "__main__":
    data_file = "Database.pickle"
    bbb = BigBrotherBank(data_file)
    bbb.Listen()



