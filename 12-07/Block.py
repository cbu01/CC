import RSAWrapper
import hashlib
import Common


class Block:
    def __init__(self, num_clients,
                 list_of_client_ids,
                 list_client_public_keys,
                 list_of_starting_amounts,
                 list_of_ending_amounts,
                 list_of_signatures,
                 previous_block_hash):
        """

        Args
            :param num_clients: Number of clients
            :param list_of_client_ids: List of client ids
            :param list_of_tuples_containing_start_and_end_amounts_for_clients:
            The list of start and end amounts in the same order as the list of clients
            :param list_of_signatures:
            List of signatures in the same order as the list of client ids
            The signatures sign the concatenation of the bytes for n, ID1, ..., IDn, (end_1-start_1), ..., (end_n-start_n)
            :param previous_block_hash (str): Hash value of the previous block
        """
        self.list_of_client_ids = list_of_client_ids
        self.list_of_signatures = list_of_signatures
        self.starting_amounts = list_of_starting_amounts
        self.ending_amounts = list_of_ending_amounts
        self.list_client_public_keys = list_client_public_keys
        self.num_clients = num_clients
        self.previous_block_hash = previous_block_hash

    def get_client_ending_amounts(self):
        return self.ending_amounts

    def get_client_ids(self):
        return self.list_of_client_ids

    def get_previous_block_hash(self):
        return self.previous_block_hash

    def verify_block(self):
        payload_verified = self.verify_payload()
        if not payload_verified:
            print "Payload not verified for block"
            return False

        return True

    def verify_payload(self):
        signature_verified = self._verify_signatures()
        amounts_verified = self._verify_amounts()

        if not signature_verified:
            print "Signature verification not working for block"

        if not amounts_verified:
            print "Amounts do not verify for block"

        return signature_verified and amounts_verified

    def _verify_signatures(self):
        """ Using public keys from the message to encrypt the signatures should match the hash of the message

        Returns:
            bool: If all signatures match the hash of the message.
        """
        message_to_sign = self._message_to_sign()
        for i in range(len(self.list_of_client_ids)):
            public_key = self.list_client_public_keys[i]
            signature = self.list_of_signatures[i]
            verified = RSAWrapper.verify(message_to_sign, signature, public_key)
            if not verified:
                print "Signature does not verify for public key " + str(public_key)
                return False

        return True

    def _verify_amounts(self):
        """ Verify that sum of starting balances is the same the the sum of the ending balances

        Returns:
            bool: If starting and ending balances sum to same number
        """
        float_threshold = 0.0001
        return abs(sum(self.starting_amounts) - sum(self.ending_amounts)) < float_threshold

    def _message_to_sign(self):
        return Common.transaction_signature_text(
            self.num_clients,
            self.list_of_client_ids,
            self.starting_amounts,
            self.ending_amounts)

    def hash_value(self):
        hasher = hashlib.sha256()
        hasher.update(str(self))
        return hasher.digest()

    def get_client_ids_starting_balance_ending_balance(self):
        """ Gets a list of tuples for the block containing (client_id, starting_balance, ending_balance)

            Returns:
                tuple: List of tuples for the block containing (client_id, starting_balance, ending_balance)
            """
        return_value = []
        for i in range(len(self.list_of_client_ids)):
            return_value.append((self.list_of_client_ids[i], self.starting_amounts[i], self.ending_amounts[i]))
        return return_value

    def __str__(self):
        return self._message_to_sign() + str(self.previous_block_hash)
