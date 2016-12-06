
def int_to_id(int_val):
    """ Takes an int and pads 0's in front of it to create a 32 char long string as id """
    int_as_string = str(int_val)
    int_as_string_len = len(int_as_string)
    return (32-int_as_string_len) * "0" + int_as_string