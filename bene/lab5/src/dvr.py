import sys

from sim import Sim
import node
import link
import packet

from network import Network

import random

class DVRApp(object):
    def __init__(self,node):
        self.node = node
        self.routingTable = {}
        entry = TableEntry()
        entry.addVector(self.node.hostname, 0)
        self.routingTable[self.node.hostname] = entry
        print routingTable 

    def receive_packet(self,packet):
        print Sim.scheduler.current_time(),self.node.hostname,packet.ident

class TableEntry(object):
	def __init__(self):
		self.missedCount = 0
		self.vectors = []

	def addVector(self, host, distance):
		self.vectors.append((host, distance))

if __name__ == '__main__':
    # parameters
	net = Network('../networks/setup.txt')

	n1 = net.get_node('n1')
    n2 = net.get_node('n2')

    myAPP = DVRApp(n1)

    