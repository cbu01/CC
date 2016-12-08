import RSAWrapper
import hashlib
import Common


class Block:
    def __init__(self, block_payload, previous_block, previous_block_hash):
        """

        Args
            :param block_payload (BlockPayload): block payload. See description in that class
            :param previous_block (Block): The previous block
            :param previous_block_hash (str): Hash value of the previous block
        """
        self.previous_block_hash = previous_block_hash
        self.previous_block = previous_block
        self.block_payload = block_payload

    def verify_block(self):
        calculated_previous_hash = self.previous_block.hash_value()
        if self.previous_block_hash != calculated_previous_hash:
            print "Hash values of previous block do not add up !"
            return False
        payload_verified = self.block_payload.verify_payload()
        if not payload_verified:
            print "Payload not verified for block"
            return False

        return True

    def hash_value(self):
        hasher = hashlib.sha256()
        hasher.update(str(self))
        return hasher.digest()

    def get_client_ids_starting_balance_ending_balance(self):
        """ Gets a list of tuples for the block containing (client_id, starting_balance, ending_balance)

            Returns:
                tuple: List of tuples for the block containing (client_id, starting_balance, ending_balance)
            """
        return [(single_account_data[0], single_account_data[1], single_account_data[2]) for single_account_data in self.block_payload.message]

    def __str__(self):
        return str(self.block_payload) + str(self.previous_block_hash)


class BlockPayload:
    def __init__(self,
                 num_clients,
                 list_of_client_ids,
                 list_client_public_keys,
                 list_of_tuples_containing_start_and_end_amounts_for_clients,
                 list_of_signatures):

        """
        :param num_clients: Number of clients
        :param list_of_client_ids: List of client ids
        :param list_of_tuples_containing_start_and_end_amounts_for_clients:
            The list of start and end amounts in the same order as the list of clients
        :param list_of_signatures:
            List of signatures in the same order as the list of client ids
            The signatures sign the concatenation of the bytes for n, ID1, ..., IDn, (end_1-start_1), ..., (end_n-start_n)
        """

        self.list_of_client_ids = list_of_client_ids
        self.list_of_signatures = list_of_signatures
        self.starting_amounts = [x[0] for x in list_of_tuples_containing_start_and_end_amounts_for_clients]
        self.ending_amounts = [x[1] for x in list_of_tuples_containing_start_and_end_amounts_for_clients]
        self.list_client_public_keys = list_client_public_keys
        self.num_clients = num_clients

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
        for i in range(len(self.list_of_client_ids)):
            public_key = self.list_client_public_keys[i]
            signature = self.list_of_signatures[i]
            verified = RSAWrapper.verify(self._message_to_sign(), signature, public_key)
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
