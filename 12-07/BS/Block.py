import RSAWrapper
import hashlib


class Block:
    def __init__(self, block_payload, previous_block, previous_block_hash):
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
    def __init__(self, str_message, message, signatures):
        # TODO missing transaction id somewhere
        """
        Args:
            str_message (str): A string representation of the message for easier signature comparison
            message (list_of_tuples): Each tuple has the format:
                (client_public_key(key_object) , starting_balance(float), ending_balance(float))
            signatures (list): A list of signatures. This list has the same ordering as the messages.
        """
        self.str_message = str_message
        self.message = message
        self.signatures = signatures

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
        for i in range(len(self.message)):
            public_key = self.message[i][0]
            signature = self.signatures[i]
            verified = RSAWrapper.verify(self.str_message, signature, public_key)
            if not verified:

                return False

        return True

    def _verify_amounts(self):
        """ Verify that sum of starting balances is the same the the sum of the ending balances

        Returns:
            bool: If starting and ending balances sum to same number
        """
        list_of_input_balances = [x[1] for x in self.message]
        input_sum = sum(list_of_input_balances)
        list_of_output_balances = [x[2] for x in self.message]
        output_sum = sum(list_of_output_balances)
        float_threshold = 0.0001
        return abs(input_sum - output_sum) < float_threshold

    def __str__(self):
        return self.str_message + ''.join(self.signatures)