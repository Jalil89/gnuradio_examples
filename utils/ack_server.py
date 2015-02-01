import socket,sys, struct
from threading import Thread

ACKED_TRUE,ACKED_FALSE,ACKED_NON = range(3)
I_FRAME,P_FRAME,B_FRAME,FILE,U_VIDEO,AUDIO = range(6)

class ack_server(object):

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 30000)
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(server_address)
        self.acked_packets_true = {}
        self.acked_packets_false = {}
    def add_pkt_type(self, pkt_type):
        self.acked_packets_true[pkt_type] = list()
        self.acked_packets_false[pkt_type] = list()
        
        
    def is_acked(self,pkt_type,pktno):
        
        if pktno in self.acked_packets_true[pkt_type]:
            return ACKED_TRUE
        elif pktno in self.acked_packets_false[pkt_type]:
            return ACKED_FALSE
        else:
            return ACKED_NON
    def handle_connection(self,connection):
        while True:
            ack = connection.recv(16)
            if not ack:
                break
            (pkt_type,) = struct.unpack('!H', ack[0:2])
            (pktno,) = struct.unpack('!H', ack[2:4])
            (ok,) = struct.unpack('!H', ack[4:6])
            if pkt_type not in [I_FRAME,P_FRAME,B_FRAME,FILE,U_VIDEO]:
                continue
            if ok == 1:
                self.acked_packets_true[pkt_type].append(pktno)
                if len(self.acked_packets_true[pkt_type]) > 20:
                    temp = self.acked_packets_true[pkt_type]
                    self.acked_packets_true[pkt_type] = temp[10:]
            else:
                self.acked_packets_false[pkt_type].append(pktno)
                if len(self.acked_packets_false[pkt_type]) > 20:
                    temp = self.acked_packets_false[pkt_type]
                    self.acked_packets_false[pkt_type] = temp[10:]
    def start(self):
        self.sock.listen(1)
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = self.sock.accept()
        thread1 = Thread(target =self.handle_connection  , args = ( connection,))
        thread1.start()
        #self.handle_connection()

