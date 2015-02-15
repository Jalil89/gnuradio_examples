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
from transceiver_utils.transmit_path import *
from transceiver_utils.receive_path import *
from bladerf_hw.bladerf_tx import *
from bladerf_hw.bladerf_rx import *
from ack_utils.ack import *

import struct, sys, os
import random, time, struct

IFF_TUN        = 0x0001   # tunnel IP packets
IFF_TAP        = 0x0002   # tunnel ethernet frames
IFF_NO_PI    = 0x1000   # don't pass extra packet info
IFF_ONE_QUEUE    = 0x2000   # beats me ;)

def open_tun_interface(tun_device_filename):
    from fcntl import ioctl
    
    mode = IFF_TAP | IFF_NO_PI
    TUNSETIFF = 0x400454ca

    tun = os.open(tun_device_filename, os.O_RDWR)
    ifs = ioctl(tun, TUNSETIFF, struct.pack("16sH", "gr%d", mode))
    ifname = ifs[:16].strip("\x00")
    return (tun, ifname)

class my_top_block(gr.top_block):
    def __init__(self, callback, options):
        gr.top_block.__init__(self)
        self.osmosdr_source = bladerf_rx(options.devicenum).get_sdr() 
        self.osmosdr_sink = bladerf_tx(options.devicenum).get_sdr()
        
        self.rxpath = receive_path(callback, options)
        self.txpath = transmit_path(options)
        
        self.connect(self.osmosdr_source, self.rxpath)
        self.connect(self.txpath, self.osmosdr_sink)
        
# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////

def main():

    global n_rcvd, n_right, oack
    n_rcvd = 0
    n_right = 0
    
    
    def send_pkt(payload='', eof=False):
        return tb.txpath.send_pkt(payload, eof)
    
    def rx_callback(ok, payload):
        global n_rcvd, n_right, oack
        n_rcvd += 1
        (pktno,) = struct.unpack('!H', payload[0:2])
        data  = payload[2:]
        if ok:
            n_right += 1
            oack.send_ack()
        print "ok: %r \t pktno: %d \t n_rcvd: %d \t n_right: %d \t n_right: %d" % (ok, pktno, n_rcvd, n_right, len(data))
   
    parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")
    
    
    parser.add_option("-a", "--args", type="string", default="",
                          help="Device args, [default=%default]")
    parser.add_option("-w", "--devicenum", type="string", default="0",
                          help="Device number, [default=%default]")
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
    parser.add_option("-r", "--role", type="string", default="receiver",
                      help="the role of the node: sender or receiver")
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
    
    digital.ofdm_mod.add_options(parser, expert_grp)
    digital.ofdm_demod.add_options(parser, expert_grp)
    transmit_path.add_options(parser, expert_grp)
    receive_path.add_options(parser, expert_grp)

    (options, args) = parser.parse_args ()

    #(tun_fd, tun_ifname) = open_tun_interface(options.tun_device_filename)

    # build the graph
    tb = my_top_block(rx_callback, options)

    r = gr.enable_realtime_scheduling()
    if r != gr.RT_OK:
        print "Warning: failed to enable realtime scheduling"

    oack = ack(send_pkt)
    tb.start()                      # start flow graph
    pktno = 1
    pkt_size = 1000
    role = options.role
    if role=='sender':
        while True:
            
            data = (pkt_size - 2) * chr(pktno & 0xff) 
            #data, addr = sock.recvfrom(1500) # buffer size is 1024 bytes
            payload1 = struct.pack('!H', pktno & 0xffff) + data
            pktno += 1
            send_pkt(payload1)
            if oack.wait_for_ack() is False:
                sys.stderr.write('x')
            else:
                sys.stderr.write('.')
    
    
    tb.wait()                       # wait for it to finish

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
