import sys
sys.path.append('..')

from src.sim import Sim
from src.node import Node
from src.link import Link
from src.transport import Transport
from src.tcp import TCP
from src.network import Network

import optparse
import os
import subprocess
#This is another comment
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

        self.run()

        self.diff(1)
        self.diff(2)
        self.diff(3)
        self.diff(4)
        self.diff(5)

    def parse_options(self):
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        parser.add_option("-f","--filename",type="str",dest="filename",
                          default='test1MB.txt',
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

    def diff(self, index):
        args = ['diff','-u',self.in_directory + '/' + self.filename,self.out_directory+'/'+self.filename+str(index)]
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
        # Sim.set_debug('Link')

        # setup application
        a1 = AppHandler(self.filename + str(1), self.out_directory)
        a2 = AppHandler(self.filename + str(2), self.out_directory)
        a3 = AppHandler(self.filename + str(3), self.out_directory)
        a4 = AppHandler(self.filename + str(4), self.out_directory)
        a5 = AppHandler(self.filename + str(5), self.out_directory)

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

        # setup connection
        c1 = TCP(t1,n1.get_address('n2'),1,n2.get_address('n1'),1,a1,window=self.window)
        c2 = TCP(t2,n2.get_address('n1'),1,n1.get_address('n2'),1,a1,window=self.window)

        # setup connection
        c3 = TCP(t1,n1.get_address('n2'),2,n2.get_address('n1'),2,a2,window=self.window)
        c4 = TCP(t2,n2.get_address('n1'),2,n1.get_address('n2'),2,a2,window=self.window)

        # setup connection
        c5 = TCP(t1,n1.get_address('n2'),3,n2.get_address('n1'),3,a3,window=self.window)
        c6 = TCP(t2,n2.get_address('n1'),3,n1.get_address('n2'),3,a3,window=self.window)

        # setup connection
        c7 = TCP(t1,n1.get_address('n2'),4,n2.get_address('n1'),4,a4,window=self.window)
        c8 = TCP(t2,n2.get_address('n1'),4,n1.get_address('n2'),4,a4,window=self.window)

        # setup connection
        c9 = TCP(t1,n1.get_address('n2'),5,n2.get_address('n1'),5,a5,window=self.window)
        c0 = TCP(t2,n2.get_address('n1'),5,n1.get_address('n2'),5,a5,window=self.window)

        # send a file
        with open(self.in_directory + '/' + self.filename,'r') as f:
            while True:
                data = f.read(10000)
                if not data:
                    break
                Sim.scheduler.add(delay=0, event=data, handler=c1.send)
                Sim.scheduler.add(delay=0.1, event=data, handler=c3.send)
                Sim.scheduler.add(delay=0.2, event=data, handler=c5.send)
                Sim.scheduler.add(delay=0.3, event=data, handler=c7.send)
                Sim.scheduler.add(delay=0.4, event=data, handler=c9.send)

        # run the simulation
        Sim.scheduler.run()


if __name__ == '__main__':
    m = Main()
