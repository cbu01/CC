import threading
from __main__ import name

class Working_Client():


    class listeningThread (threading.Thread):
        def __init__(self, threadID, name):
            self.threadID = threadID
            self.name = name
        
        def run(self):
            print "listeningThread is active"
        