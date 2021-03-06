import sys

from sim import Sim
from node import Node
from link import Link
from transport import Transport
from tcp import TCP
from network import Network

import optparse
import os
import subprocess

class AppHandler(object):
    def __init__(self,filename, directory):
        self.filename = filename
        self.directory = directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.f = open("%s/%s" % (self.directory,self.filename),'w')

    def receive_data(self,data):
        #Sim.trace('AppHandler',"application got %d bytes" % (len(data)))
        self.f.write(data)
        self.f.flush()

class Main(object):
    def __init__(self):
        # iterations = 1
        self.out_directory = '../output/received'
        self.in_directory = '../data'
        self.parse_options()
        #print self.filename
        # self.total = 0.0;
        # for i in range(0, iterations):
        #     self.run()
        for windowSize in [1000]:#, 2000, 5000, 10000, 15000, 20000]:
            # print "--Results with window size " + str(windowSize)
            #self.window = windowSize
            self.run()

        # print "Average over " + str(iterations) + " iterations: " + str(self.total / float(iterations))

        self.diff()

    def parse_options(self):
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        parser.add_option("-f","--filename",type="str",dest="filename",
                          default='test.txt',
                          help="filename to send")

        parser.add_option("-l","--loss",type="float",dest="loss",
                          default=0.0,
                          help="random loss rate")

        parser.add_option("-w","--window",type="int",dest="window",
                          default=1000,
                          help="transmission window size")

        (options,args) = parser.parse_args()
        self.filename = options.filename
        self.loss = options.loss
        self.window = options.window

    def diff(self):
        args = ['diff','-u',self.in_directory + '/' + self.filename,self.out_directory+'/'+self.filename]
        result = subprocess.Popen(args,stdout = subprocess.PIPE).communicate()[0]
        #print
        if not result:
            pass
            #print "File transfer correct!"
        else:
            print "File transfer failed. Here is the diff:"
            print
            print result

    def run(self):
        # parameters
        Sim.scheduler.reset()
        Sim.set_debug('AppHandler')
        Sim.set_debug('TCP')

        # setup network
        net = Network('../networks/setup.txt')
        net.loss(self.loss)

        # setup routes
        n1 = net.get_node('n1')
        n2 = net.get_node('n2')
        n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
        n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

        # setup transport
        t1 = Transport(n1)
        t2 = Transport(n2)

        # setup application
        a = AppHandler(self.filename, self.out_directory)

        # setup connection
        c1 = TCP(t1,n1.get_address('n2'),1,n2.get_address('n1'),1,a,window=self.window)
        c2 = TCP(t2,n2.get_address('n1'),1,n1.get_address('n2'),1,a,window=self.window)

        # send a file
        with open(self.in_directory + '/' + self.filename,'r') as f:
            while True:
                data = f.read(10000)
                if not data:
                    break
                Sim.scheduler.add(delay=0, event=data, handler=c1.send)

        # run the simulation
        Sim.scheduler.run()
        # print str(self.window) + " & " + \
        #         str(Sim.scheduler.current_time()) + " & " + \
        #         str(4116160.0 / float(Sim.scheduler.current_time())) + " & " + \
        #         str(c2.totalQueueingDelay / float(c1.totalPacketsSent)) + " \\\\"

        # print str(self.window) + "," + str(4116160.0 / float(Sim.scheduler.current_time()))

        #print str(self.window) + "," + str(c2.totalQueueingDelay / float(c1.totalPacketsSent))

        # print "Ave Queueing Delay: " + str(c2.totalQueueingDelay / float(c1.totalPacketsSent))
        # print "Throughput: " + str(4116160.0 / float(Sim.scheduler.current_time()))
        # self.total += Sim.scheduler.current_time()

if __name__ == '__main__':
    m = Main()
