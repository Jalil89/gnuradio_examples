import sys
sys.path.append("./..")

import tsparseimpl.tsparser as tsparser


TS_PACKET_SIZE = 188
TS_PACKETS_PER_IP = 7


TRUE = 1
FALSE = 0

I_FRAME = 2
P_FRAME = 3
B_FRAME = 4
DATA = 5

NON_TS_PACKET = 6
TS_PACKET = 7

I_FRAME_DATA = 8
P_FRAME_DATA = 9
B_FRAME_DATA = 10

class PacketParser(object):
    def __init__(self):
        self._current_packet = FALSE
        

    
    def get_packet_type(self, packet_raw):
        l = list()
        if len(packet_raw) != TS_PACKET_SIZE*TS_PACKETS_PER_IP:
            return NON_TS_PACKET, l
        for i in range(7):
            tspacket = packet_raw[i*TSPACKETSIZE:(i+1)*TSPACKETSIZE]
            p_type = tsparser.ts_get_type(tspacket)
            if p_type == DATA or p_type == FALSE:
                if self._current_packet == I_FRAME:
                    p_type = I_FRAME_DATA
                elif self._current_packet == P_FRAME:
                    p_type = P_FRAME_DATA
                elif self._current_packet == B_FRAME:
                    p_type = B_FRAME_DATA
                else:
                    print "unknown packet"
            else:
                self._current_packet = p_type 
            l.append(p_type)
        return TS_PACKET, l
        


