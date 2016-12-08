import hashlib

def int_to_id(int_val):
    """ Takes an int and pads 0's in front of it to create a 32 char long string as id """
    int_as_string = str(int_val)
    int_as_string_len = len(int_as_string)
    return (32-int_as_string_len) * "0" + int_as_string


def transaction_signature_text(num_clients, list_of_client_ids, list_of_client_start_balances, list_of_client_end_balances):
    message = str(num_clients)

    for client_id in list_of_client_ids:
        message += str(client_id)

    for i in range(list_of_client_start_balances):
        start_balance = list_of_client_start_balances[i]
        end_balance = list_of_client_end_balances[i]
        message += str(end_balance - start_balance)

    return message


def client_id_from_public_key(public_key):
    hasher = hashlib.sha256()
    hasher.update(public_key)
    return hasher.digest()