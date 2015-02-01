import osmosdr

class bladerf_tx(object):
    def __init__(self, which = "0"):
        self._symbol_rate = 20000000
        self._center_freq = 2400000000
        self._txvga1_gain = -4
        self._txvga2_gain = 25
        
    
    def get_sdr(self):
        out = osmosdr.sink(args="bladerf=0,buffers=128,buflen=32768,fpga=/usr/share/Nuand/bladeRF/hostedx40.rbf")
        out.set_sample_rate(self._symbol_rate)
        out.set_center_freq(self._center_freq, 0)
        out.set_freq_corr(0, 0)
        out.set_gain(self._txvga2_gain, 0)
        out.set_bb_gain(self._txvga1_gain, 0)
        out.set_bandwidth(26000000, 0)
        return out
    
    
