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
        for line in f.readlines():
            if line.startswith("#"):
                continue
            try:
                t, event = line.split()
            except:
                continue
            t = float(t)
            event = str(event)
            packet = (t, event)
            self.data.append(packet)
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
        xDrop = []
        yDrop = []
        queueSize = 0
        for t, event in self.data:
            if event == 'E':
                queueSize += 1
                x.append(t)
                y.append(queueSize)
            elif event == 'D':
                queueSize -= 1
                x.append(t)
                y.append(queueSize)
            else:
                #This is a dropped packet
                xDrop.append(t)
                yDrop.append(queueSize + 1)

            
        scatter(x,y,marker='s',s=1)
        # scatter(ackX,ackY,marker='d',s=.5)
        scatter(xDrop,yDrop,marker='x',s=100)
        xlabel('Time (seconds)')
        ylabel('Queue Size (packets)')	## ========	 EDIT THIS LABEL
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
