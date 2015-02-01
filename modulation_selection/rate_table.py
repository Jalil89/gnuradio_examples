from modulation import *
import random

BEST_THROUGHPUT, SECOND_BEST_THROUGHPUT, BEST_PROBABILITY, BASE_RATE, RANDOM_RATE, NONE = range(5)
NORMAL_MODE, LOOKAROUND_MODE = range(2)

class rate_table(object):
    
    # modulations should be sorted in ascending order according 
    # to their rate.  E.g bpsk, qpsk, 8psk, qam16 
    def __init__(self, modulations, lookaround_rate): 
        self._modulations = modulations
        modulation = self._modulations[0] # choose any modulation initially
        self._best_throughput = modulation
        self._base_rate = modulation
        self._second_best_throughput = modulation
        self._best_probability = modulation
        self._random_rate = random.choice(self._modulations)
        self._mode = NORMAL_MODE
        self._current_rate = 0
        self._lookaround_rate = lookaround_rate
        self._normal_rate = [
                             self._best_throughput, self._best_throughput,
                             self._second_best_throughput, self._second_best_throughput,
                             self._best_probability, self._best_probability,
                             self._base_rate, self._base_rate  
                             ]
        self._lookaround_rate = [
                             self._random_rate, self._random_rate,
                             self._second_best_throughput, self._second_best_throughput,
                             self._best_probability, self._best_probability,
                             self._base_rate, self._base_rate
                             ]
        
        
    def update_table(self,ewma_level):
        throughput_table = {}
        probability_table = {}
        for modulation in self._modulations:
            throughput  = modulation.calculate_throughput(ewma_level)
            probability = modulation.get_probability()
            throughput_table[throughput] = modulation
            probability_table[probability] = modulation
        throughput_list = throughput_table.keys()
        probability_list = probability_table.keys()
        throughput_list.sort()
        probability_list.sort()
        self._best_throughput = throughput_list[0]
        self._second_best_throughput = throughput_list[1]
        self._best_probability = probability_list[0]
        self._base_rate = self._modulations[0]
        self._random_rate = random.choice(self._modulations)

        
    def set_transmission_status(self, success, bytes):
        """
        if self._current_rate == BEST_THROUGHPUT:
            self.set_best_throughput_status(success, bytes)
        elif self._current_rate == SECOND_BEST_THROUGHPUT:
            self.set_second_best_throughput_status(success, bytes)
        elif self._current_rate == BEST_PROBABILITY:
            self.set_best_probability_status(success, bytes)
        elif self._current_rate == RANDOM_RATE:
            self.set_random_rate_status(success, bytes)
        elif self._current_rate == BASE_RATE:
            self.set_base_rate_status(success, bytes)
        """
        if self._mode == NORMAL_MODE:
            s = len(self._normal_rate)
            modulation = self._normal_rate[self._current_rate] 
            modulation.packet_transmitted(success, bytes)
        else:
            s = len(self._normal_rate)
            modulation = self._lookaround_rate[self._current_rate] 
            modulation.packet_transmitted(success, bytes)
        if success:
              self.reset_rate()
        else:
              self._current_rate = (self._current_rate+1) % s
        
    
    
    # fix this func
    def reset_rate(self):
        if random.randint(0,int(self._lookaround_rate/100.0)) == 0:
            self.reset_lookaround_mode()
        else:
            self.reset_normal_mode()
    
    def get_modulation(self):
        if self._mode == NORMAL_MODE:
            return self._normal_rate[self._current_rate]
        else:
            return self._lookaround_rate[self._current_rate]
        
    def reset_normal_mode(self):
        self._current_rate = 0
        self._mode = NORMAL_MODE
    
    def reset_lookaround_mode(self):
        self._current_rate = 0
        self._mode = LOOKAROUND_MODE           
        
    """    
    def set_base_rate_status(self, success, bytes):
        self._base_rate.packet_transmitted(success, bytes)
        
    def set_best_throughput_status(self, success, bytes):
        self._best_throughput.packet_transmitted(success, bytes)
    
    def set_second_best_throughput_status(self, success, bytes):
        self._second_best_throughput.packet_transmitted(success, bytes)
        
    def set_best_probability_status(self, success, bytes):
        self._best_probability.packet_transmitted(success, bytes)
        
    def set_random_rate_status(self,success,bytes):
        self._random_rate.packet_transmitted(success, bytes)
    """    
        