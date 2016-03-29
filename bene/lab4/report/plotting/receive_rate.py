import optparse
import sys

import matplotlib
import numpy as np
from pylab import *
from sets import Set

# Parses a file of rates and plot a sequence number graph. Black
# squares indicate a sequence number being sent and dots indicate a
# sequence number being ACKed.
class Plotter:
    def __init__(self,file,output):
        """ Initialize plotter with a file name. """
        self.file = file
        self.output = output
        self.data = []
        self.port_count = 0
        self.min_time = None
        self.max_time = None

    def parse(self):
        """ Parse the data file """
        f = open(self.file)
        port_set = Set([])
        for line in f.readlines():
            if line.startswith("#"):
                continue
            try:
                t, port = line.split()
            except:
                continue
            t = float(t)
            port = int(port)
            self.data.append((t, port))
            port_set.add(port)
            if not self.min_time or t < self.min_time:
                self.min_time = 0
            if not self.max_time or t > self.max_time:
                self.max_time = t
            self.port_count = len(port_set)

    def plot(self):
        """ Create a sequence graph of the packets. """
        clf()
        figure(figsize=(15,5))

        x = [[] for v in range(self.port_count)]
        y = [[] for v in range(self.port_count)]

        for p in range(1, self.port_count + 1):
            print "Examining Port " + str(p)
            for slot in np.arange(.1, (self.max_time + .1), .1):
                upper = min(slot, self.max_time)
                lower = max(0, slot - 1)
                subset = [val[0] for val in self.data if (val[0] <= upper and val[0] > lower and val[1] == p)]
                rate = (len(subset) * 1000 * 8) / (upper - lower)
                rate /= 1000    # to get it into kb
                print str(slot) + " -- " + str(rate) + " -- " + str(upper) + " -- " + str(lower)
                x[p-1].append(slot)
                y[p-1].append(rate)

        # for (t,sequence,flag) in self.data:
        #     if flag == "A":
        #         ackX.append(t)
        #         ackY.append((sequence / 1000) % 50)
        #     elif flag == "T":
        #         mapXY[sequence] = t
        #         # print mapXY
        #     elif flag == "X":
        #         # get the map entry
        #         # put that in drop lists
        #         drop_time = mapXY[sequence]
        #         dropX.append(drop_time)
        #         dropY.append((sequence / 1000) % 50)

        #     for k in mapXY.keys():
        #         x.append(mapXY[k])
        #         y.append((k / 1000) % 50)

            # x.append(t)
            # y.append(sequence % (1000*50))
            # # pretend the ACK came 0.2 seconds later
            # ackX.append(t + 0.2)
            # ackY.append(sequence % (1000*50))
            
        for p in range(0, self.port_count):
            scatter(x[p],y[p],marker='s',s=10)
        # scatter(ackX,ackY,marker='d',s=.5)
        # scatter(dropX,dropY,marker='x',s=100)
        xlabel('Time (seconds)')
        ylabel('Receive Rate (Kbps)')	## ========	 EDIT THIS LABEL
        xlim([self.min_time,self.max_time])
        savefig(self.output)						## ========= EDIT THIS FILE NAME


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