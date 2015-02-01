import queue
import socket,sys
import struct

# Create a TCP/IP socket
from senderlog import *

I_FRAME,P_FRAME,B_FRAME,FILE,U_VIDEO,AUDIO = range(6)

class queue_allocator(object):
    def __init__(self, queue):
        self.queue = queue
        self.logf = senderlog()

    def insertToQueue(self,q_id,p):
        q = self.queue.getQueue(q_id)
        packet = p
        cwmin,cwmax,rt = q.get_params()
        packet = struct.pack('!H', rt & 0xffff) + packet
        packet = struct.pack('!H', cwmax & 0xffff) + packet
        packet = struct.pack('!H', cwmin & 0xffff) + packet

        self.queue.insertPacket(q_id, packet)
        
    
        
    def allocate_queue(self,packet,pktno):
        p = packet
        # fix
        (pkt_type,) = struct.unpack('!H', p[0:2])
        p = struct.pack('!H', pktno & 0xffff) + p
        
        #print "insert packet to queue %d" % pkt_type
        q_id = ""   
        if pkt_type == I_FRAME:
            q_id = "High"
        elif pkt_type == P_FRAME:
            q_id = "Medium"
        elif pkt_type == B_FRAME:
            q_id = "Low"
        elif pkt_type == FILE:
            q_id = "DT"
        elif pkt_type == U_VIDEO:
            q_id = "ET"
        elif pkt_type == AUDIO:
            q_id = "AU"
        self.logf.log(pkt_type,pktno)
        self.insertToQueue(q_id, p)
        
