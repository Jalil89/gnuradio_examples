import time
import threading

class queue(object):
    def __init__(self,priority,cwmin, cwmax, rt):
        self.cwmin = cwmin
        self.cwmax = cwmax
        self.rt = rt
        self.size = 0
        self.queue = []
        self.priority = priority
        self.counter = 0
        self.delay = 0
        
    def getMacParams(self):
        return self.cwmin,self.cwmax,self.rt
    
    def addPacket(self, e):
        self.queue.append(e)
        if self.size == 0:
            self.counter = self.priority
            self.delay = time.time() 
        self.size+=1
        
    
    def update(self):
        if self.size != 0:
            self.delay = time.time() - self.delay
            self.counter += self.priority
            
    def getPacket(self):
        if self.size != 0:
            packet = self.queue.pop(0)
            self.size-=1
            if self.size == 0:
                self.delay = 0
            self.counter = 0
            return packet
    
    def get_params(self):
        return self.cwmin,self.cwmax,self.rt
    

    
    def getdelay(self):
        return self.delay
    
    def getcounter(self):
        return self.counter
    
    def getsize(self):
        return self.size
            


class queueList(object):
    def __init__(self):
        self.queues = {  "High"     : queue(7,7,15,8,) , # 6
                         "Medium"   : queue(5,15,31,8,) , # 3
                         "Low"      : queue(3,31,1023,4) , # 2
                         "DT"       : queue(2,31,1023,4) ,
                         "ET"       : queue(5,15,31,8) ,
                         #"ET"       : queue(1,31,1023,7,0) ,
                         "AU"       : queue(4,7,15,7) 
                       }
        self.lock = threading.Lock()
    
    def getQueue(self, qid):
        return self.queues[qid]
        
    def insertPacket(self, qid, packet):
        self.lock.acquire()
        q = self.queues[qid]
        q.addPacket(packet)
        self.lock.release()
        
    def update(self):
        self.lock.acquire()
        items = self.queues.items()
        for i in items:
            q_id, q = i
            q.update()
        self.lock.release()
        
    def getPackets(self, numOfPackets):
        self.lock.acquire()
        #print "get packet"
        items = self.queues.keys()
        packets = list()
        q_ids = []
        n = 0
        for i in range(numOfPackets):
            n  = 0
            maxq_id = None
            maxq_counter = 0
            for i in items:
                q_id = i
                qu = self.queues[i]
                counter = qu.getcounter()
                if counter > maxq_counter:
                    maxq_counter = counter
                    maxq_id = q_id    
            if maxq_id != None:
                n+=1
                selected_q = self.queues[maxq_id]
                q_ids.append(maxq_id)
                packets.append(selected_q.getPacket())
        self.lock.release()
        self.update()
        
        return packets 
            
            
        