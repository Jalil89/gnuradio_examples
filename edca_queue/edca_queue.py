from threading import Thread
import time

from packet import *

class edca_queue(object):
    def __init__(self,def_delay):
        self._smallest_unit=0.001
        self._queue = list()
        self._process_queue = Thread(target =self.process_queue  , args = ( ))
        self._process_queue.start()
        self._def_delay = def_delay
    
	
	def process_queue(self):
		while True:
			for pkt in self._queue:
				deadln = pkt.get_deadline()
				deadln -= self._smallest_unit
				if deadln <= 0.0:
					self._queue.remove(pkt)
				else:
					pkt.set_deadline()
			time.sleep(self._smallest_unit)
        
    def enqueue(self, payload, deadline = self._def_delay):
        p = packet(payload)
        p.set_deadline(deadline)
        self._queue.append(p)
    
    def isempty(self):
        return len(self._queue) == 0    
        
    def top(self):
        p = self._queue[0] 
        min_deadln = p.get_deadline()
        for pkt in self._queue:
            deadln = pkt.get_deadline()
            if deadln < min_deadln:
                p = pkt
                min_deadln = deadln
        return p
    
    def pop(self,p):
        self._queue.remove(p)
        
class best_effort_queue(object):
    def __init__(self):
        self._queue = list()
    
    def enqueue(self,payload):
        self._queue.append(packet(payload))

    def isempty(self):
        return len(self._queue) == 0
    
    def top(self):
        return self._queue[0]
    
    def pop(self,p):
		return self._queue.remove(p)
	
        

    
        