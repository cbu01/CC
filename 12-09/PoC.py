import threading


        
class Thread1(threading.Thread):
       
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
      
    def run(self):
        print self.name
        super_name
            
            
class Thread2(threading.Thread):
        
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
      
    def run(self):
        print self.name
        print super_name
            
    

super_name = "I AM YOUR FATHER"
        
son1 = Thread1(1,"Son_1")
son2 = Thread2(2,"Son_2")
son1.start()
son2.start() 