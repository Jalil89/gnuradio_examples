#!/usr/bin/env python
#
# Copyright 2005,2006,2011,2013 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 





import osmosdr
import socket
from gnuradio import gr
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from gnuradio.gr.pubsub import pubsub
from optparse import OptionParser
import time, struct, sys

from gnuradio import digital
from gnuradio import blocks

# from current dir
from transmit_path import transmit_path


import sys
import math
import numpy
import random
import time



class my_top_block(gr.top_block,pubsub):
    
    
    def __init__(self, options):
        gr.top_block.__init__(self)
        
        self.sink = self._setup_osmosdr(options)
        
        self.txpath = transmit_path(options)

        self.connect(self.txpath, self.sink)
        
    def _setup_osmosdr(self, options):
        symbol_rate = 20000000
        center_freq = 2400000000
        txvga1_gain = -4
        txvga2_gain = 25

        out = osmosdr.sink(args="bladerf=0,buffers=128,buflen=32768,fpga=/usr/share/Nuand/bladeRF/hostedx40.rbf")
        out.set_sample_rate(symbol_rate)
        #bw = out.get_bandwidth()
        #print bw
        out.set_center_freq(center_freq, 0)
        out.set_freq_corr(0, 0)
        out.set_gain(txvga2_gain, 0)
        out.set_bb_gain(txvga1_gain, 0)
        out.set_bandwidth(26000000, 0)
        
        return out
    

    def set_samp_rate(self, sr):
        sr = self._sink.set_sample_rate(sr)
        return True

    

    def set_bandwidth(self, bw):
        bw_ranges = self._sink.get_bandwidth_range()
        clipped_bw = bw_ranges.clip(bw)
        if self._sink.get_bandwidth() != clipped_bw:
            bw = self._sink.set_bandwidth(clipped_bw)
        
            if self._verbose:
                print "Set bandwidth to:", bw

    def set_dc_offset(self):
        correction = complex( 0.0, 0.0 )

        try:
            self._sink.set_dc_offset( correction )

            if self._verbose:
                print "Set DC offset to", correction
        except RuntimeError as ex:
            print ex

    def set_iq_balance(self):
        correction = complex( 0.0, 0.0 )

        try:
            self._sink.set_iq_balance( correction )

            if self._verbose:
                print "Set IQ balance to", correction
        except RuntimeError as ex:
            print ex

    def set_freq(self, freq):
        freq = self._sink.set_center_freq(freq)
        if freq is not None:
            self._freq = freq
        return freq

    def set_freq_corr(self, ppm):
        ppm = self._sink.set_freq_corr(ppm)
        
# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////

def main():

    def send_pkt(payload='', eof=False):
        return tb.txpath.send_pkt(payload, eof)
    
    def send_pkt_hm(payload1='',payload2='', eof=False):
        return tb.txpath.send_pkt_hm(payload1, payload2)
    
    def set_modulation(modulation):
        tb.txpath.set_modulation(modulation)

    parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")
    parser.add_option("-a", "--args", type="string", default="",
                      help="Device args, [default=%default]")
    parser.add_option("-A", "--antenna", type="string", default=None,
                      help="Select Rx Antenna where appropriate")
    parser.add_option("-s", "--samp-rate", type="eng_float", default=None,
                      help="Set sample rate (bandwidth), minimum by default")
    parser.add_option("-g", "--gain", type="eng_float", default=None,
                      help="Set gain in dB (default is midpoint)")
    parser.add_option("-G", "--gains", type="string", default=None,
                      help="Set named gain in dB, name:gain,name:gain,...")
    parser.add_option("-f", "--tx-freq", type="eng_float", default=None,
                      help="Set carrier frequency to FREQ [default=mid-point]",
                      metavar="FREQ")
    parser.add_option("-c", "--freq-corr", type="int", default=None,
                      help="Set carrier frequency correction [default=0]")
    parser.add_option("", "--amplitude", type="eng_float", default=0.8,
                      help="Set output amplitude to AMPL (0.1-1.0) [default=%default]",
                      metavar="AMPL")
    parser.add_option("-v", "--verbose", action="store_true", default=False,
                      help="Use verbose console output [default=%default]")
	
    """
    parser.add_option("-a", "--args", type="string", default="",
                      help="Device args, [default=%default]")
    parser.add_option("-A", "--antenna", type="string", default=None,
                      help="Select RX antenna where appropriate")
    parser.add_option("-s", "--samp-rate", type="eng_float", default=None,
                      help="Set sample rate (bandwidth), minimum by default")
    parser.add_option("-f", "--center-freq", type="eng_float", default=None,
                      help="Set frequency to FREQ", metavar="FREQ")
    parser.add_option("-M", "--megabytes", type="eng_float", default=1.0,
                      help="set megabytes to transmit [default=%default]")
    parser.add_option("","--discontinuous", action="store_true", default=False,
                      help="enable discontinuous mode")
    parser.add_option("","--from-file", default=None,
                      help="use intput file for packet contents")
    parser.add_option("","--to-file", default=None,
                      help="Output file for modulated samples")
	"""
    transmit_path.add_options(parser, expert_grp)
    digital.ofdm_mod.add_options(parser, expert_grp)

    (options, args) = parser.parse_args ()

    # build the graph
    tb = my_top_block(options)
    
    r = gr.enable_realtime_scheduling()
    if r != gr.RT_OK:
        print "Warning: failed to enable realtime scheduling"

    tb.start()                       # start flow graph
    
    # generate and send packets
    nbytes = int(1e6 * 1000)
    n = 0
    pktno = 0
    pkt_size = 500

    

    UDP_IP = "localhost"
    UDP_PORT = 32000

                     
    #sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    #sock.bind((UDP_IP, UDP_PORT))
    
    
    time_start = int(round(time.time() * 100))
    packets = 0
    set_modulation("qpsk")
    while True:
        
        data = (pkt_size - 2) * chr(pktno & 0xff) 
        #data, addr = sock.recvfrom(1500) # buffer size is 1024 bytes
        payload1 = struct.pack('!H', pktno & 0xffff) + data
        pktno += 1
        payload2 = struct.pack('!H', pktno & 0xffff) + data
        pktno += 1
        send_pkt_hm(payload1, payload1)
        #send_pkt(payload1)
        n += len(payload1)+len(payload2)
        sys.stderr.write('.')
        
        packets+=2
    time_end =  int(round(time.time() * 1000))
    print "\n time elapsed is %d milliseconds " % (time_end-time_start)
        
    send_pkt(eof=True)
    time.sleep(2)               # allow time for queued packets to be sent
    tb.wait()                   # wait for it to finish

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
