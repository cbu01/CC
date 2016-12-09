import threading

class PoC(object):
    
    
    class Thread1(threading.Thread):
        
        def __init__(self, threadID, name):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
      
        def run(self):
            print self.name
            print self.self.super_name
            
            
    class Thread2(threading.Thread):
        
        def __init__(self, threadID, name):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
      
        def run(self):
            print self.name
            print self.self.super_name
            
    
    def __init__(self):
        self.super_name = "I AM YOUR FATHER"
        
        self.son1 = self.Thread1(1,"Son_1")
        self.son2 = self.Thread2(2,"Son_2")
        
        self.son1.start()
        self.son2.start() 