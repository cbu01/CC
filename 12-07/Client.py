import pickle, socket, os, sys
import RSAWrapper
from Crypto.PublicKey import RSA
import Common


class Client:
    def __init__(self, name):
        self._global_client_register_name = "client_register.pickle"
        self.name = name
        self.BBBhost = "localhost"
        self.BBBport = 10555

        self._BBB_key = RSA.importKey(open("BBBPublicKey.pem", "r"))

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._key, self._ID = self._load_keys(str(name) + "PrivateKey.pem")

    #######################################################################

    def __sendMessage(self, message):
        signature = RSAWrapper.sign(message, self._key)
        p_message = pickle.dumps((message, signature))
        encMessage = RSAWrapper.encrypt(p_message, self._BBB_key)
        self.s.sendto(encMessage, (self.BBBhost, self.BBBport))
        return

    def __receiveMessage(self):
        message, addr = self.s.recvfrom(2048)
        decMessage = RSAWrapper.decrypt(message, self._key)
        print "decMessage" + str(decMessage)
        u_message, signature = pickle.loads(decMessage)
        print "picMessage" + str(u_message)
        validSignature = RSAWrapper.verify(u_message, signature, self._BBB_key)
        if (validSignature):
            return u_message
        else:
            print "WARNING: Invalid Signature!!!"
            return u_message

    #######################################################################

    def __pay(self, target_name, amount):
        try:
            a = float(amount)  # cast amount to float
            if (a <= 0):
                print "transaction not successful - choose a positive amount of money"
            else:
                target_client_id = self._get_client_id_from_global_name(target_name)
                if target_client_id == "":
                    return
                message = pickle.dumps(("PAY", self._ID, target_client_id, a))
                self.__sendMessage(message)
                reply = self.__receiveMessage()
                if (reply == "False"):
                    print "transaction not successfull - rejected by BBB"
                    return
                else:
                    print "transaction successful with transaction ID: " + str(reply)
                    return
        except ValueError as e:
            print "transaction not successful - enter amount as a number"
            print e
            return

    def __query(self, source_client_name, transactionID, amount):
        try:
            a = float(amount)  # cast amount to float
            source_client_id = self._get_client_id_from_global_name(source_client_name)

            message = pickle.dumps(("QUERY", self._ID, source_client_id, Common.int_to_id(transactionID), amount))
            self.__sendMessage(message)
            reply = self.__receiveMessage()
            if (reply == "True"):
                print "Money received"
                return
            else:
                print "Money has not been received"
                return
        except ValueError:
            print "transaction not successful - enter amount as a number"
            return

    ######################################################################

    def _data_file_exists(self, data_file_name):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, data_file_name)
        return os.path.isfile(file_path)

    def _load_keys(self, key_file_name):
        key_file_exists = self._data_file_exists(key_file_name)
        if not key_file_exists:
            _key = RSAWrapper.keygen()
            file = open(key_file_name, "w+")
            file.write(_key.exportKey('PEM'))
            file.close()
            client_id = self._register(_key.publickey(), _key)
            pickle.dump(client_id, open(self.name + "_settings.pickle", "wb"))
        else:
            _key = RSA.importKey(open(key_file_name, "r"))
            client_id = pickle.load(open(self.name + "_settings.pickle", "rb"))

        return _key, client_id

    def _register(self, _public_key, client_private_key):
        e_key = _public_key.exportKey()
        r_message = pickle.dumps(("REGISTER", "", e_key))
        enc_r_message = RSAWrapper.encrypt(r_message, self._BBB_key)
        self.s.sendto(enc_r_message, (self.BBBhost, self.BBBport))  # DON'T sign key!!!

        reply, addr = self.s.recvfrom(2048)
        decMessage = RSAWrapper.decrypt(reply, client_private_key)
        u_message, signature = pickle.loads(decMessage)
        validSignature = RSAWrapper.verify(u_message, signature, self._BBB_key)
        if (validSignature):
            if (u_message != "False"):
                print "Successfully registered"
                self._add_client_to_global_client_register(u_message)
                return u_message
            else:
                print "Registration not possible"
                sys.exit(0)
                return
        else:
            print "Unable to verify bank signature"
            return

    #######################################################################

    def _add_client_to_global_client_register(self, client_id):
        try:
            global_client_dict = pickle.load(open(self._global_client_register_name, "rb"))
        except:
            global_client_dict = {}

        global_client_dict[self.name] = client_id
        pickle.dump(global_client_dict, open(self._global_client_register_name, "wb"))

    def _get_client_id_from_global_name(self, client_name):
        try:
            global_client_dict = pickle.load(open(self._global_client_register_name, "rb"))
            return global_client_dict[client_name]
        except:
            return ""

    def mainLoop(self):
        loop = True
        while loop:
            x = raw_input(">: ").split()
            print x
            if (x[0] == "pay"):
                self.__pay(x[1], x[2])
            elif (x[0] == "query"):
                self.__query(x[1], x[2], x[3])
            elif (x[0] == "quit"):
                loop = False
            else:
                print "Please enter something useful"
