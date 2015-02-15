

# class that has info about modulation

class modulation(object):
    def __init__(self, name = None, rate = None, packet_air_time = 0):
        self._name = name 
        self._rate = rate # in bitspersecond
        self._P = 0
        self._packet_air_time = packet_air_time
        self._total_packets_transmitted = 1.0
        self._packets_transmitted_successfully = 0.0
        self._megabits_transmitted = 0.0
        
    def packet_transmitted(self, success, bytes):
        if success:
            self._packets_transmitted_successfully+=1
        self._total_packets_transmitted+=1
        self._megabits_transmitted += bytes*8/1000000.0 
    
    def _get_success_prob(self):
        return (self._packets_transmitted_successfully/self._total_packets_transmitted)
    
    
    def _reset_transmission_history(self):
        self._total_packets_transmitted = 1.0
        self._packets_transmitted_successfully = 0.0
        
    
    def calculate_throughput(self,ewma_level):
        if self._total_packets_transmitted == 1.0:
            self._P= self._calculate_ewma(ewma_level)
        self.reset()
        return (self._P * self._megabits_transmitted) / self._packet_air_time
    
    def _calculate_ewma(self, ewma_level):
        Pold = self._P
        Psuccess = self._get_success_prob()
        Pnew = (Psuccess*(100-ewma_level) + Pold* ewma_level) / 100.0
        return Pnew
    
    def get_probability(self):
        return self._P
    
    def get_air_time(self):
        return self._packet_air_time
        
    def set_name(self, name):
        self._name = name
        
    def get_name(self):
        return self._name
    
    def set_rate(self,rate):
        self._rate = rate
        
    def get_rate(self):
        return self._rate