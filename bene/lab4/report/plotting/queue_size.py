import optparse
import sys

import matplotlib
import numpy as np
from pylab import *

# Parses a file of rates and plot a sequence number graph. Black
# squares indicate a sequence number being sent and dots indicate a
# sequence number being ACKed.
class Plotter:
    def __init__(self,file):
        """ Initialize plotter with a file name. """
        self.file = file
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

	"""
	loop in increments of .1 starting at .1 and going through the end of the transmission time
		for each increment, 	set the upper bound to min(this time, last time stamp)
							, 	set the lower bound to max(0, this time - 1)
							rate = (total in that range * 1000) / (upper - lower)
	"""						

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

        """for slot in np.arange(.1, (self.max_time + .1), .1):
        	upper = min(slot, self.max_time)
        	lower = max(0, slot - 1)
        	subset = [val for val in self.data if (val <= upper and val > lower)]
        	rate = (len(subset) * 1000 * 8) / (upper - lower)
        	rate /= 1000	# to get it into kb
        	print str(slot) + " -- " + str(rate) + " -- " + str(upper) + " -- " + str(lower)
        	x.append(slot)
        	y.append(rate)
        """
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
            
        scatter(x,y,marker='s',s=1)
        # scatter(ackX,ackY,marker='d',s=.5)
        scatter(xDrop,yDrop,marker='x',s=100)
        xlabel('Time (seconds)')
        ylabel('Queue Size (packets)')	## ========	 EDIT THIS LABEL
        xlim([self.min_time,self.max_time])
        savefig('1f_queue.png')						## ========= EDIT THIS FILE NAME


def parse_options():
        # parse options
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        parser.add_option("-f","--file",type="string",dest="file",
                          default=None,
                          help="file")

        (options,args) = parser.parse_args()
        return (options,args)


if __name__ == '__main__':
    (options,args) = parse_options()
    ratefile = None
    if options.file == None:
        ratefile = "rates.txt"
        # print "plot.py -f file"
        # sys.exit()
    else:
        ratefile = options.file

    p = Plotter(ratefile)
    p.parse()
    p.plot()
