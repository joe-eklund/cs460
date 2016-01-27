import sys
sys.path.append('../..')

from src.sim import Sim
from src import node
from src import link
from src import packet

from networks.network import Network

import random

class Generator(object):
    def __init__(self,node,destination,load,duration):
        self.node = node
        self.load = load
        self.duration = duration
        self.start = 0
        self.ident = 1

    def handle(self,event):
        # quit if done
        now = Sim.scheduler.current_time()
        if (now - self.start) > self.duration:
            return

        # generate a packet
        self.ident += 1
        p = packet.Packet(destination_address=destination,ident=self.ident,protocol='delay',length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=self.node.send_packet)
        # schedule the next time we should generate a packet
        Sim.scheduler.add(delay=random.expovariate(self.load), event='generate', handler=self.handle)

class DelayHandler(object):

    def __init__(self, inFile=None):
        self.toWrite = inFile

    def receive_packet(self,packet):
        if self.toWrite is None:
            print Sim.scheduler.current_time(),packet.ident,packet.created,Sim.scheduler.current_time() - packet.created,packet.transmission_delay,packet.propagation_delay,packet.queueing_delay
        else:
            outputLine = ','.join(str(x) for x in [Sim.scheduler.current_time(),packet.ident,packet.created,Sim.scheduler.current_time() - packet.created,packet.transmission_delay,packet.propagation_delay,packet.queueing_delay])
            self.toWrite.write(outputLine + '\n')

def setupNetwork():
    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../networks/3.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

    return n1, n2, net

def makeFile(value):
    fileEnding = str(3 + value)
    if value <= .9:
        fileEnding = fileEnding + "0"

    # create an output file
    newFile = open('../output/' + fileEnding + '_out.csv', 'w')
    newFile.write('a,b,c,d,e,f,g')
    return newFile

if __name__ == '__main__':
    
    values = [.1, .2, .3, .4, .5, .6,
              .7, .8, .9, .95, .98]

    for value in values:
        n1, n2, net = setupNetwork()

        # create output file
        newFile = makeFile(value)

        # setup app
        d = DelayHandler(newFile)

        net.nodes['n2'].add_protocol(protocol="delay",handler=d)

        # calculate values for transmission delay and load
        max_rate = 1000000/(1000*8)
        load = value*max_rate

        # setup packet generator
        destination = n2.get_address('n1')
        g = Generator(node=n1,destination=destination,load=load,duration=10)
        Sim.scheduler.add(delay=0, event='generate', handler=g.handle)
        
        # run the simulation
        Sim.scheduler.run()

        newFile.close()