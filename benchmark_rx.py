#!/usr/bin/env python
#
# Copyright 2006,2007,2011,2013 Free Software Foundation, Inc.
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
from optparse import OptionParser

from gnuradio import blocks
from gnuradio import digital

# from current dir
from receive_path import receive_path
from bladerf_hw import *

import struct, sys

class my_top_block(gr.top_block):
    def __init__(self, callback,callback_msb, callback_lsb, options):
        gr.top_block.__init__(self)
        """
        symbol_rate = 20000000
        center_freq = 2400000000
        txvga1_gain = -4
        txvga2_gain = 25
        
        self.corr = corr = 0
        self.gain = gain = 40.0
        self.osmosdr_source_0 = osmosdr.source( args="bladerf=1,buffers=128,buflen=32768,fpga=/usr/share/Nuand/bladeRF/hostedx40.rbf" )
        self.osmosdr_source_0.set_sample_rate(symbol_rate)
        self.osmosdr_source_0.set_center_freq(center_freq, 0)
        self.osmosdr_source_0.set_freq_corr(corr, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(0, 0)
        self.osmosdr_source_0.set_gain(gain, 0)
        self.osmosdr_source_0.set_gain(6, "LNA")
        self.osmosdr_source_0.set_gain(30, "VGA1")
        self.osmosdr_source_0.set_gain(30, "VGA2")
        range = self.osmosdr_source_0.get_gain_range("LNA")
        print "%s gain range: start %d stop %d step %d" % ("LNA", range.start(), range.stop(), range.step())
        range = self.osmosdr_source_0.get_gain_range("VGA1")
        print "%s gain range: start %d stop %d step %d" % ("VGA1", range.start(), range.stop(), range.step())
        range = self.osmosdr_source_0.get_gain_range("VGA2")
        print "%s gain range: start %d stop %d step %d" % ("VGA1", range.start(), range.stop(), range.step())
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna("", 0)
        self.osmosdr_source_0.set_bandwidth(26000000, 0)
        """
        self.osmosdr_source = bladerf_rx('0').get_sdr() 
        self.osmosdr_sink = bladerf_tx('0').get_sdr()
        
        self.rxpath = receive_path(callback,callback_msb, callback_lsb, options)
        self.txpath = transmit_path(options)
        
        
        self.connect(self.osmosdr_source, self.rxpath)
        self.connect(self.txpath, self.osmosdr_sink)
    """
    def set_dc_offset(self):
        correction = complex( 0.0, 0.0)

        try:
            self.src.set_dc_offset( correction )
        except RuntimeError as ex:
            print ex


    def set_iq_balance(self):
        correction = complex( 0.0, 0.0 )

        try:
            self.src.set_iq_balance( correction )


        except RuntimeError as ex:
            print ex

    def set_sample_rate(self, samp_rate):
        samp_rate = self.src.set_sample_rate(samp_rate)

        try:
            self[BWIDTH_KEY] = self.set_bandwidth(samp_rate)
        except RuntimeError:
            pass

        return samp_rate

    def get_gain_names(self):
        return self.src.get_gain_names()

    def set_named_gain(self, gain, name):
        if gain is None:
            g = self[GAIN_RANGE_KEY(name)]
            gain = float(g.start()+g.stop())/2
            return

        gain = self.src.set_gain(gain, name)

    def set_bandwidth(self, bw):
        clipped_bw = self[BWIDTH_RANGE_KEY].clip(bw)
        if self.src.get_bandwidth() != clipped_bw:
            bw = self.src.set_bandwidth(clipped_bw)

        return bw

    def set_freq_from_callback(self, freq):
        freq = self.src.set_center_freq(freq)
        self[CENTER_FREQ_KEY] = freq;

    def set_freq(self, freq):
        if freq is None:
            f = self.src.get_freq_range()
            freq = float(f.start()+f.stop())/2.0
            print "Using auto-calculated mid-point frequency"
            self[CENTER_FREQ_KEY] = freq
            return

        freq = self.src.set_center_freq(freq)
        return freq

    def set_freq_corr(self, ppm):
        ppm = self.src.set_freq_corr(ppm)
    """
# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////

def main():

    global n_rcvd, n_right, sock
    
    UDP_IP = "localhost"
    UDP_PORT = 5005
    n_rcvd = 0
    n_right = 0

    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    def rx_callback(ok, payload):
        global n_rcvd, n_right, sock
        n_rcvd += 1
        (pktno,) = struct.unpack('!H', payload[0:2])
        data  = payload[2:]
        if ok:
            n_right += 1
        print "ok: %r \t pktno: %d \t n_rcvd: %d \t n_right: %d \t n_right: %d" % (ok, pktno, n_rcvd, n_right, len(data))
        #if len(data)!=1316:
            #return
        #sock.sendto(data, (UDP_IP, UDP_PORT))
        

        if 0:
            printlst = list()
            for x in payload[2:]:
                t = hex(ord(x)).replace('0x', '')
                if(len(t) == 1):
                    t = '0' + t
                printlst.append(t)
            printable = ''.join(printlst)

            print printable
            print "\n"
            
    def rx_callback_msb(ok, payload):
        global n_rcvd, n_right, sock
        n_rcvd += 1
        (pktno,) = struct.unpack('!H', payload[0:2])
        data  = payload[2:]
        if ok:
            n_right += 1
        print "MSB ok: %r \t pktno: %d \t n_rcvd: %d \t n_right: %d \t n_right: %d" % (ok, pktno, n_rcvd, n_right, len(data))
        #print "\n\n\n"
        #print ''.join(format(ord(x), 'b') for x in data)
        #print "\n\n\n"
        #if len(data)!=1316:
            #return
        #sock.sendto(data, (UDP_IP, UDP_PORT))
        

        if 0:
            printlst = list()
            for x in payload[2:]:
                t = hex(ord(x)).replace('0x', '')
                if(len(t) == 1):
                    t = '0' + t
                printlst.append(t)
            printable = ''.join(printlst)

            print printable
            print "\n"
            
    def rx_callback_lsb(ok, payload):
        global n_rcvd, n_right, sock
        n_rcvd += 1
        (pktno,) = struct.unpack('!H', payload[0:2])
        data  = payload[2:]
        if ok:
            n_right += 1
        print "LSB ok: %r \t pktno: %d \t n_rcvd: %d \t n_right: %d \t n_right: %d" % (ok, pktno, n_rcvd, n_right, len(data))
        #if len(data)!=1316:
            #return
        #sock.sendto(data, (UDP_IP, UDP_PORT))
        

        if 0:
            printlst = list()
            for x in payload[2:]:
                t = hex(ord(x)).replace('0x', '')
                if(len(t) == 1):
                    t = '0' + t
                printlst.append(t)
            printable = ''.join(printlst)

            print printable
            print "\n"

    parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")
    
    """
    parser.add_option("","--discontinuous", action="store_true", default=False,
                      help="enable discontinuous")
    parser.add_option("","--from-file", default=None,
                      help="input file of samples to demod")


    """
    
    parser.add_option("-a", "--args", type="string", default="",
                          help="Device args, [default=%default]")
    parser.add_option("-A", "--antenna", type="string", default=None,
                      help="Select RX antenna where appropriate")
    parser.add_option("-s", "--samp-rate", type="eng_float", default=None,
                      help="Set sample rate (bandwidth), minimum by default")
    parser.add_option("-f", "--center-freq", type="eng_float", default=None,
                      help="Set frequency to FREQ", metavar="FREQ")
    parser.add_option("-c", "--freq-corr", type="eng_float", default=None,
                      help="Set frequency correction (ppm)")
    parser.add_option("-g", "--gain", type="eng_float", default=None,
                      help="Set gain in dB (default is midpoint)")
    parser.add_option("-G", "--gains", type="string", default=None,
                      help="Set named gain in dB, name:gain,name:gain,...")
    parser.add_option("-r", "--record", type="string", default="/tmp/name-f%F-s%S-t%T.cfile",
                      help="Filename to record to, available wildcards: %S: sample rate, %F: center frequency, %T: timestamp, Example: /tmp/name-f%F-s%S-t%T.cfile")
    parser.add_option("", "--dc-offset-mode", type="int", default=None,
                      help="Set the RX frontend DC offset correction mode")
    parser.add_option("", "--iq-balance-mode", type="int", default=None,
                      help="Set the RX frontend IQ imbalance correction mode")
    parser.add_option("-W", "--waterfall", action="store_true", default=False,
                      help="Enable waterfall display")
    parser.add_option("-F", "--fosphor", action="store_true", default=False,
                      help="Enable fosphor display")
    parser.add_option("-S", "--oscilloscope", action="store_true", default=False,
                      help="Enable oscilloscope display")
    parser.add_option("", "--avg-alpha", type="eng_float", default=1e-1,
                      help="Set fftsink averaging factor, default=[%default]")
    parser.add_option("", "--averaging", action="store_true", default=False,
                      help="Enable fftsink averaging, default=[%default]")
    parser.add_option("", "--ref-scale", type="eng_float", default=1.0,
                      help="Set dBFS=0dB input value, default=[%default]")
    parser.add_option("", "--fft-size", type="int", default=1024,
                      help="Set number of FFT bins [default=%default]")
    parser.add_option("", "--fft-rate", type="int", default=30,
                      help="Set FFT update rate, [default=%default]")
    parser.add_option("-v", "--verbose", action="store_true", default=False,
                      help="Use verbose console output [default=%default]")
    receive_path.add_options(parser, expert_grp)
    #uhd_receiver.add_options(parser)
    digital.ofdm_demod.add_options(parser, expert_grp)

    (options, args) = parser.parse_args ()


    # build the graph
    tb = my_top_block(rx_callback,rx_callback_msb, rx_callback_lsb, options)

    r = gr.enable_realtime_scheduling()
    if r != gr.RT_OK:
        print "Warning: failed to enable realtime scheduling"

    tb.start()                      # start flow graph
    tb.wait()                       # wait for it to finish

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
