from modulation import *
from rate_table import *
import random
import copy

from threading import Thread
import time


class minstrel_legacy(object):
    def __init__(self, ewma_level, modulation_list, lookaround_rate, segment_size ):
        self._rate_table_map = {}
        self._ewma_level = ewma_level
        self._lookaround_rate = lookaround_rate
        self._receiver_id = 0
        self._modulation_list = modulation_list
        self._segment_size = segment_size
        throughput_monitoring_thread = Thread(target =self.monitor_throughput  , args = ( ))
        throughput_monitoring_thread.start()
        
    def monitor_throughput(self):
        time.sleep(0.1) # monitor 10 times a second
        receiver_ids = self._rate_table_map.keys()
        for r_id in receiver_ids:
            rate_table = self._rate_table_map[r_id]
            rate_table.update_table()
        
    def _make_rate_table(self):
        if len(self._modulation_list) < 2:
            print "no modulation to choose from. Need at least two modulations"
        modulations = copy.copy(self._modulation_list)
        return rate_table(modulations)
        
    def get_new_receiver_id(self):
        self._receiver_id += 1
        return self._receiver_id
        
        
    def add_receiver(self, receiver_id):
        rate_table = self._make_rate_table()
        self._rate_table_map[receiver_id] = rate_table
        
    def set_transmission_status(self, receiver_id, status, bytes):
        rate_table = self._rate_table_map[receiver_id]
        rate_table.set_transmission_status(status, bytes) 
        
    def update_tables(self):
        receivers = self._rate_table_map.keys()
        for r in receivers:
            rt = self._rate_table_map[r]
            rt.update_table(self._ewma_level)
            
    def get_modulation(self, receiver_id):
        rt = self._rate_table_map[receiver_id]
        return rt.get_modulation()
    
    
        
    