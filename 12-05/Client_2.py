from Client import Client

if __name__ == "__main__":
    c = Client({31*"0" + "2"})
    c.mainLoop()
