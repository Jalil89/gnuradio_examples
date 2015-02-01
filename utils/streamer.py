import socket,sys
import struct
from threading import Thread
import time

from queue_allocation import *
from queue import *

I_FRAME,P_FRAME,B_FRAME,FILE,U_VIDEO,AUDIO = range(6)

class streamer(object):
    def __init__(self,name, filename,pkt_type,kbs,qa):
        self.filename = filename
        self.pkt_type = pkt_type
        self.kbs = kbs
        self.name = name
        self.qa = qa
        self.pktno = 0
        
    def start(self):
        print self.name
        self.f = open(self.filename,"rb")
        print "start streaming"
        thread = Thread(target =self.stream , args = ( ))
        thread.start()
        #self.stream()
    def stream(self):
        self.pktno += 1
        data = self.f.read(996)
        while len(data)>0:
            p = struct.pack('!H', self.pkt_type & 0xffff) + data
            #print "%s : allocating a packet" % self.name
            self.qa.allocate_queue(p,self.pktno)
            time.sleep(1.0/self.kbs)
            self.pktno += 1
            data = self.f.read(996)
            
class h264streamer(object):
    def __init__(self,name, filename,kbs,qa):
        self.filename = filename
        self.kbs = kbs
        self.name = name
        self.qa = qa
        self.pktno = 0
        
    def start(self):
        print self.name
        self.f = open(self.filename,"rb")
        print "start streaming"
        
        thread = Thread(target =self.stream , args = ( ))
        thread.start()

    def stream(self):
        time.sleep(10)
        self.pktno += 1
        data = self.f.read(998)
        while len(data)>0:
            p = data
            #print "%s : allocating a packet" % self.name
            self.qa.allocate_queue(p,self.pktno)
            time.sleep(1.0/self.kbs)
            self.pktno += 1
            data = self.f.read(998)
            
            
            
            