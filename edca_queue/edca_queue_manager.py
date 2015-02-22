from edca_queue import *
import os
import sys
sys.path.append("./..")
from packet_parser.parse_packet import *
from threading import Thread
import time

from 80211mac import *

IPHEADERSIZE = 20

videorate = 163000.0

class QueueManager(object):
    def __init__(self, tunfd):
        
        self._queues = {  "AC0"      : edca_queue(0.05) ,
                          "AC1"      : edca_queue(0.1) ,
                          "AC2"      : edca_queue(0.2) ,
                          "AC3"      : best_effor_queue()  
                       }
        self._tunfd = tunfd
        self._mac = Mac80211()
        self._parser = PacketParser()
        self._read_data_thread = Thread(target =self.enrich_queues  , args = ( ))
        self._read_data_thread.start()
        self._tx_thread = Thread(target =self.tx_packets  , args = ( ))
        self._tx_thread.start()
        
    def enrich_queues(self):
        while 1:
            payload = os.read(self.tunfd, 10*1024)
            raw_packet = self._detach_header(payload) 
            qid = self.get_packet_queue()
            q = self._queues[qid]
            q.enqueue(payload, ((8*(1316+IPHEADERSIZE))/videorate)-0.01)
            
    def _detach_header(self,packet):
        return packet[IPHEADERSIZE:]
    
    def get_packet_queue(self, packet):
        raw_packet = self._detach_header(packet)
        type, list = self._parser.get_packet_type(raw_packet)
        if type == NON_TS_PACKET:
            return "AC3"
        # processing TS packet
        if type in [I_FRAME, P_FRAME, B_FRAME, I_FRAME_DATA]:
            return "AC0"
        elif type == P_FRAME_DATA:
            return "AC1"
        else:
            return "AC2"
    
    def _get_packet(self):
        qids = self.
    
    def tx_packets(self):
        while 1:
            
            
        
    
    
		
		