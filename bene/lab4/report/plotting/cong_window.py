import optparse
import sys

import matplotlib
import numpy as np
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
        f = open(self.file)
        port_to_use = 2
        for line in f.readlines():
            if line.startswith("#"):
                continue
            try:
                t, port, window = line.split()
            except:
                continue
            if int(port) != port_to_use:
                continue
            t = float(t)
            window = int(window)
            self.data.append((t, window))
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
        for t, window in self.data:
            x.append(t)
            y.append(window)

        scatter(x,y,marker='s',s=1)
        # scatter(ackX,ackY,marker='d',s=.5)
        # scatter(xDrop,yDrop,marker='x',s=100)
        xlabel('Time (seconds)')
        ylabel('Congestion Window Size (bytes)')
        xlim([self.min_time,self.max_time])
        savefig(self.output)


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
