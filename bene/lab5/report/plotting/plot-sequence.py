import optparse
import sys

import matplotlib
from pylab import *

# Parses a file of rates and plot a sequence number graph. Black
# squares indicate a sequence number being sent and dots indicate a
# sequence number being ACKed.
class Plotter:
    def __init__(self,file,output):
        """ Initialize plotter with a file name. """
        self.file = file
        self.output = output
        self.data = []
        self.min_time = None
        self.max_time = None

    def parse(self):
        """ Parse the data file """
        first = None
        port_to_use = 2
        f = open(self.file)
        for line in f.readlines():
            if line.startswith("#"):
                continue
            try:
                t,port,sequence,flag = line.split()
            except:
                continue
            if int(port) != port_to_use:
                continue
            t = float(t)
            sequence = int(sequence)
            flag = str(flag)
            self.data.append((t,sequence,flag))
            if not self.min_time or t < self.min_time:
                self.min_time = 0
            if not self.max_time or t > self.max_time:
                self.max_time = t

    def plot(self):
        """ Create a sequence graph of the packets. """
        clf()
        figure(figsize=(15,5))
        x = []
        y = []
        ackX = []
        ackY = []
        dropX = []
        dropY = []
        mapXY = {}
        for (t,sequence,flag) in self.data:
            if flag == "A":
                ackX.append(t)
                ackY.append((sequence / 1000) % 50)
            elif flag == "T":
                mapXY[sequence] = t
                # print mapXY
            elif flag == "X":
                # get the map entry
                # put that in drop lists
                drop_time = mapXY[sequence]
                dropX.append(drop_time)
                dropY.append((sequence / 1000) % 50)

            for k in mapXY.keys():
                x.append(mapXY[k])
                y.append((k / 1000) % 50)

            # x.append(t)
            # y.append(sequence % (1000*50))
            # # pretend the ACK came 0.2 seconds later
            # ackX.append(t + 0.2)
            # ackY.append(sequence % (1000*50))
            
        scatter(x,y,marker='s',s=10)
        scatter(ackX,ackY,marker='d',s=.5)
        scatter(dropX,dropY,marker='x',s=100)
        xlabel('Time (seconds)')
        ylabel('(Sequence Number / 1000) Mod 50')
        xlim([self.min_time,self.max_time])
        savefig(self.output)                        ## ========= EDIT THIS FILE NAME


def parse_options():
        # parse options
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        parser.add_option("-i","--input",type="string",dest="input",
                          default=None,
                          help="input")

        parser.add_option("-o","--output",type="string",dest="output",
                          default=None,
                          help="output")

        (options,args) = parser.parse_args()
        return (options,args)


if __name__ == '__main__':
    (options,args) = parse_options()

    p = Plotter(options.input, options.output)
    p.parse()
    p.plot()