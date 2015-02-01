import osmosdr

class bladerf_rx(object):
    def __init__(self, which = "0"):
        self._symbol_rate = 20000000
        self._center_freq = 2400000000
        self._txvga1_gain = -4
        self._txvga2_gain = 25
        self._which = which
        
    def get_sdr(self):
        corr = 0
        gain = 40.0
        osmosdr_source_0 = osmosdr.source( args="bladerf="+self._which+",buffers=128,buflen=32768,fpga=/usr/share/Nuand/bladeRF/hostedx40.rbf" )
        osmosdr_source_0.set_sample_rate(self._symbol_rate)
        osmosdr_source_0.set_center_freq(self._center_freq, 0)
        osmosdr_source_0.set_freq_corr(corr, 0)
        osmosdr_source_0.set_dc_offset_mode(0, 0)
        osmosdr_source_0.set_iq_balance_mode(0, 0)
        osmosdr_source_0.set_gain_mode(0, 0)
        osmosdr_source_0.set_gain(gain, 0)
        osmosdr_source_0.set_gain(6, "LNA")
        osmosdr_source_0.set_gain(30, "VGA1")
        osmosdr_source_0.set_gain(30, "VGA2")
        range = osmosdr_source_0.get_gain_range("LNA")
        print "%s gain range: start %d stop %d step %d" % ("LNA", range.start(), range.stop(), range.step())
        range = osmosdr_source_0.get_gain_range("VGA1")
        print "%s gain range: start %d stop %d step %d" % ("VGA1", range.start(), range.stop(), range.step())
        range = osmosdr_source_0.get_gain_range("VGA2")
        print "%s gain range: start %d stop %d step %d" % ("VGA1", range.start(), range.stop(), range.step())
        osmosdr_source_0.set_if_gain(20, 0)
        osmosdr_source_0.set_bb_gain(20, 0)
        osmosdr_source_0.set_antenna("", 0)
        osmosdr_source_0.set_bandwidth(26000000, 0)
        
        return osmosdr_source