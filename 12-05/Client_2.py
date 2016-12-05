from Client import Client
import Common

if __name__ == "__main__":
    c = Client(Common.int_to_id(1))
    c.mainLoop()
