import tsparser
import sys

filename = sys.argv[1]

TSPACKETSIZE = 188

f = open(filename,"rb")

line = f.read(1316)

while len(line)>0:
    for i in range(7):
        tspacket = line[i*TSPACKETSIZE:(i+1)*TSPACKETSIZE]
        #print len(tspacket)
        print  tsparser.ts_get_type(tspacket),
    
    line = f.read(1316)


close(f)