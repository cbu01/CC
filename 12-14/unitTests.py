import Utilities


def inverse_mod_test():
    number = 3
    mod = 17
    result = Utilities.inverse(number, mod)
    expected_result = 6
    if result != expected_result:
        raise Exception("Expected a result of 6 but got a result of " + str(result))


if __name__ == "__main__":
    inverse_mod_test()