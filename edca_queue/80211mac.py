import sys
sys.path.append("./..")

from modulation_selection import *
from ack_utils import *


class Mac80211(object):
    def __init__(self, tx):
        self._tx = tx
        self._ack = ack()
        
    def get_ack_callback(self):
        return self._ack.ack_callback
    
    def send_pkt(self, rt_count):
        count = 0
        while count < rt_count:
            self._tx.send_pkt()
            if self._ack.wait_for_ack():
                break
            count+=1
        
    
    
        
        
        
        
        
