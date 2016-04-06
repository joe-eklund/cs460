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
        entry.addVector(self.node.get_address(node.hostname), 0)
        self.routingTable[self.node.get_address(node.hostname)] = entry

        print self.routingTable
        for v in self.routingTable[self.node.hostname].vectors:
            print v
        # TODO: schedule the first broadcast for right now

    def receive_packet(self,packet):
        # update the routing table
        # also add forwarding table entries
        neighbor_table = packet.body
        hasChanged = False
        tableKeys = self.routingTable.keys()

        for neighbor, entries in neighbor_table:  # loop through the table
            if neighbor not in tableKeys:



        # if there are changes, broadcast them to neighbors
        print Sim.scheduler.current_time(),self.node.hostname,packet.ident

    def broadcast(self,reschedule=True):
        # for each link, send a copy of the routingTable using a packet with protocol "dvr"

        # TODO: schedule this function to happen again in 30 seconds
        pass

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

    