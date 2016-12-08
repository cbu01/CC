"""This class is for testing purposes only. It creates a few initial clients
    which represent the founders of the currency."""
    
from Client import Client
import os


import os

def cleandir():
    for files in os.listdir('.'):
        for f in files:
            if f.endswith(".pickle") or f.endswith(".pem"):
                print "file " + f + " would be removed"
                #os.remove(f)

def launchBBB():
    
    original = client("Original") # This is the source of all money!!!
    # make the first transaction to this account
    
    
    # just a few other clients
    client_1 = Client("mannsi")
    client_2 = Client("caro")
    client_3 = Client("chuck_norris")
    client_4 = Client("Alpha")