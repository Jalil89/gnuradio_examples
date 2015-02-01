import socket,sys
import struct

class ack_client(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = ('localhost', 30000)
        print >>sys.stderr, 'connecting to %s port %s' % server_address
        self.sock.connect(server_address)
        
    def ack(self,pkt_type, pktno,ackstatus):
        ack = 10*'x'
        ack = struct.pack('!H', ackstatus & 0xffff) + ack
        ack = struct.pack('!H', pktno & 0xffff) + ack
        ack = struct.pack('!H', pkt_type & 0xffff) + ack
        self.sock.sendall(ack)