import time

current_micro_time = lambda: int(round(time.time()))


class ack(object):
    def __init__(self, tx_callback):
        self._tx_callback = tx_callback
        self._is_waiting = False
        self._ack_timeout = 1000 # 1 millisecond
        self._ack_sequence = 16 * 'x'
        
    def wait_for_ack(self):
        self._is_waiting = True
        last_time = current_micro_time()
        while self._is_waiting and  current_micro_time() - last_time < 1000:
            continue
        if self._is_waiting:
            self._ack_timeout = False
            return False
        else:
            return True
        
    
    def send_ack(self):
        self._tx_callback(self._ack_sequence)    
    
    def ack_callback(self,ack_msg):
        if ack_msg == self._ack_sequence:
            self._is_waiting = False
        
        