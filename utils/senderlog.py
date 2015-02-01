import sys, struct,time

I_FRAME,P_FRAME,B_FRAME,FILE,U_VIDEO,AUDIO = range(6)

class senderlog(object):
    def __init__(self):
        self.logf_file = open("filesender_log.txt","w")
        self.logf_video = open("videosender_log.txt", "w")
        self.logf_mp4 = open("mp4sender_log.txt","w")
        
    def log(self,pkt_type,pktno):
        ctime = time.time()
        print pkt_type
        if pkt_type in [I_FRAME,P_FRAME,B_FRAME]:
            #print "%f %d %d\n" % (ctime,pktno,pkt_type)
            self.logf_mp4.write("%f %d %d\n" % (ctime,pktno,pkt_type))
            self.logf_mp4.flush()
        elif pkt_type == FILE:
            self.logf_file.write("%f %d\n" % (ctime,pktno))
            self.logf_file.flush()
        elif pkt_type == U_VIDEO:
            self.logf_video.write("%f %d\n" % (ctime,pktno))
            self.logf_video.flush()
            
