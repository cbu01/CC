import pickle
import socket
import os
import os.path
import time
import RSAWrapper
from Crypto.PublicKey import RSA
import hashlib
import Common


class BigBrotherBank:
    def __init__(self, data_file_name):
        self._key = self._load_keys("BBBPrivateKey.pem")
        self._client_public_keys = {}  # Stores {client_id, exported_client_public_key_that_needs_importing_to_work}
        self._data_file_name = data_file_name
        self._balances_dict = {}
        self._transactions_dict = {}
        self._next_transaction_int_id = 100
        self._load_data_from_file()
        self._host = "localhost"
        self._port = 10555
       

        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._s.bind((self._host,self._port))

    def authorize(self, param_list):

        n = param_list[0]
        m = param_list[1]
        
        paying_ids = [param_list[2+2*x] for x in range(n)]
        paying_amounts = [param_list[3+2*x] for x in range(n)]
        receiving_ids = [param_list[2+2*x+2*n] for x in range(m)]
        receiving_amounts = [param_list[3+2*x+2*n] for x in range(m)]
        signature_list = param_list[2+(2*n)+(2*m):]
   
        # TODO make sure every paying client exists in the system
        sender_id_exists = all([(paying_ids[x] in self._client_public_keys) for x in range(n)])
        if not(sender_id_exists):
            print "sender id does not exist"
            return None
        # ensure that every receiving client exists
        receiver_id_exists = all([(receiving_ids[x] in self._client_public_keys) for x in range(m)])
        if not(receiver_id_exists):
            print "receiver id does not exit"
            return None
        # TODO make sure every paying account has enough balance
        enough_balance = all([(self._balances_dict[paying_ids[x]] >= paying_amounts[x] and paying_amounts[x] >= 0) for x in range(n)])
        if not(enough_balance):
            print "not enough money"
            return None       
        # make sure that the total paying amount is equal to the total receiving amounts    
        total_amount_to_send = sum(paying_amounts)
        total_amount_to_receive = sum(receiving_amounts)
        if total_amount_to_send != total_amount_to_receive:
            print "amounts to send and receive do not match"
            return None
        # check if all signatures are valid
        # therefore I interpret all input values as strings
        # assume id_x belongs to signature_x
        list_without_signatures = param_list[:len(param_list)-len(signature_list)]
        list_to_sign = "".join([str(list_without_signatures[x]) for x in range(len(list_without_signatures))])
        
        signatures_valid = all([RSAWrapper.verify(list_to_sign, signature_list[x], RSA.importKey(self._client_public_keys[paying_ids[x]])) for x in range(n)])
        if not(signatures_valid):
            print "signature not valid"
            return None
        else: 
            for x in range(n):
                self._balances_dict[paying_ids[x]] -= float(paying_amounts[x]) # withdraw money
            for y in range(m):
                self._balances_dict[receiving_ids[y]] += float(receiving_amounts[y]) # receive money
            # Save the transaction
            transaction_id = self._generate_transaction_id()
            self._transactions_dict[transaction_id] = ((paying_ids, receiving_ids, paying_amounts, receiving_amounts, time.time()))
            self._save_data_to_file()

            return transaction_id
        
        
        

    def verify(self, ID_out, x, transaction_ID):
        try:
            payment_information = self._transactions_dict[transaction_ID]
            if (len(payment_information) == 5):
                receiving_ids = payment_information[1]
                receiving_amounts = payment_information[3]
                number_of_receivements = receiving_ids.count(ID_out)
                indices = []
                for  n in range(number_of_receivements):
                    i = receiving_ids.index(ID_out)
                    receiving_ids.pop(i)
                    indices.append(i)
                for j in indices:
                    if (receiving_amounts[j] == x):
                        return True
                return False
            else:
                receiving_id = payment_information[1]
                receiving_amount = payment_information[2]
                if (ID_out == receiving_id and x == receiving_amount):
                    return True
            return False
        except ValueError:
            return False
                     
            
            
        
 
            

    def pay(self, id1, id2, amount):
        """ Returns a transaction id if id1 can transfer amount to id2.
            Returns False otherwise or if something went wrong """
        print "Got payment request from id1: {0}, id2:{1} and amount: {2}".format(id1, id2, amount)

        amount = float(amount)
        if amount <= 0:
            print "Attempt to pay a negative amount of money!"
            return False

        if id1 not in self._balances_dict:
            # Id1 does not exist in system
            print "id1 is unknown"
            return False

        if id2 not in self._balances_dict:
            print "id2 is unknown"
            # Id2 does not exist in system
            return False

        id1_balance = self._balances_dict[id1]
        if id1_balance < amount:
            # Id1 does not have the funds to transfer the money
            print "not enough money to transfer"
            return False

        # Update the amounts
        self._balances_dict[id1] -= amount
        self._balances_dict[id2] += amount

        # Save the transaction
        transaction_id = self._generate_transaction_id()
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

    def register_client(self, client_public_key):
        client_id = self._generate_client_id(client_public_key)
        if client_id in self._client_public_keys:
            # Client is already registered, not cool
            return False

        self._client_public_keys[client_id] = client_public_key
        self._balances_dict[client_id] = 10
        self._save_data_to_file()
        return client_id

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
        self._save_data_to_file()

    def _generate_transaction_id(self):
        self._next_transaction_int_id += 1
        return Common.int_to_id(self._next_transaction_int_id)
        #return uuid.uuid4().hex

    def _generate_client_id(self, client_public_key):
        hasher = hashlib.sha256()
        hasher.update(client_public_key)
        return hasher.digest()

    def _load_keys(self, key_file_name):
        key_file_exists = self._data_file_exists(key_file_name)
        if not key_file_exists:
            _key = RSAWrapper.keygen()
            public_key = _key.publickey()
            f_priv = open(key_file_name, "w+")
            f_priv.write(_key.exportKey('PEM'))
            f_priv.close()
            f_pub = open("BBBPublicKey.pem", "w+")
            f_pub.write(public_key.exportKey('PEM'))
            f_pub.close()
        else:
            _key = RSA.importKey(open(key_file_name, "r"))

        return _key
    
    #########################################################################
    
    def __sendMessage(self, message, receiver, receiverID):
        signature = RSAWrapper.sign(message, self._key)
        receiver_string_key = self._client_public_keys[receiverID]
        receiver_Key = RSA.importKey(receiver_string_key)
        p_s_message = pickle.dumps((message,signature))
        encMessage = RSAWrapper.encrypt(p_s_message, receiver_Key)
        self._s.sendto(encMessage, receiver)
        return

    def __receiveMessage(self):
        message, addr = self._s.recvfrom(2048)
        decMessage = RSAWrapper.decrypt(message, self._key) # decrypt
        picMessage = pickle.loads(decMessage) # pickle
        print "decMessage " + str(decMessage)
        print "picMessage" + str(picMessage)
        print "picMessage type" + str(type(picMessage))
        print "type of picMessage" + str(type(picMessage))
        # check if this is a signed message (tuple) or a key (not a tuple)
        if picMessage[0] == "REGISTER": # then this is a key which is NOT signed
            senderID = picMessage[1]
            print "receivedMessage1 " + str(picMessage) + " " + str(senderID)
            return picMessage, addr, senderID
        else :
            command = picMessage[0]
            signature = picMessage[1]
            picCommand = pickle.loads(command) # unpack command
            print "picCommand" + str(picCommand)
            senderID = picCommand[1] # get id
            sender_Key = RSA.importKey(self._client_public_keys[senderID]) # get key
            validSignature = RSAWrapper.verify(command, signature, sender_Key)
            if (validSignature):
                print "receivedMessage2 " + str(picCommand) + " " + str(senderID)
                return picCommand, addr, senderID
            else: 
                print "WARNING: Invalid Signature!!!"
                return picCommand, addr, senderID
        
    ########################################################################

    def Listen(self):
        while True:
            message, addr, senderID = self.__receiveMessage()
            if message[0] == "PAY" and len(message) == 4:
                try: 
                    a = message[3]
                    success = self.pay(message[1], message[2], message[3])
                    self.__sendMessage(str(success), addr, senderID)
                except ValueError:
                    self.__sendMessage(str(False), addr, senderID)
            elif message[0] == "QUERY" and len(message) == 5:
                try:
                    a = float(message[4])
                    sender_id = message[2]
                    receiver_id = message[1]
                    transaction_id = message[3]
                    amount = message[4]
                    success = self.query(sender_id, receiver_id, transaction_id, amount)
                    self.__sendMessage(str(success), addr, senderID)
                except ValueError:
                    self.__sendMessage(str(False), addr, senderID)
            elif message[0] == "REGISTER" and len(message) == 3:
                senderID = self.register_client(message[2])
                if  senderID:
                    self.__sendMessage(senderID, addr, senderID)
            else:
                self.__sendMessage(str(False), addr, senderID)
                
    #######################################################################


if __name__ == "__main__":
    data_file = "Database.pickle"
    bbb = BigBrotherBank(data_file)
    bbb.Listen()
