import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet

from networks.network import Network

import random

class DelayHandler(object):
	def receive_packet(self,packet):
		""",packet.ident,Sim.scheduler.current_time() - packet.created"""
		print Sim.scheduler.current_time(),packet.created,packet.transmission_delay,packet.propagation_delay,packet.queueing_delay

def setupNetwork(path):
	# parameters
	Sim.scheduler.reset()

	# setup network
	net = Network(path)

	# setup routes
	n1 = net.get_node('n1')
	n2 = net.get_node('n2')
	n3 = net.get_node('n3')
	n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
	n1.add_forwarding_entry(address=n3.get_address('n2'),link=n1.links[0])
	n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])
	n2.add_forwarding_entry(address=n3.get_address('n2'),link=n2.links[1])
	n3.add_forwarding_entry(address=n1.get_address('n2'),link=n3.links[0])
	n3.add_forwarding_entry(address=n2.get_address('n3'),link=n3.links[0])

	# setup app
	d = DelayHandler()
	net.nodes['n1'].add_protocol(protocol="delay",handler=d)
	net.nodes['n2'].add_protocol(protocol="delay",handler=d)
	net.nodes['n3'].add_protocol(protocol="delay",handler=d)
	return n1, n2, n3, net

def prt1():


	n1, n2, n3, net = setupNetwork('./networks/2-1.txt')

	queuePackets(1000, n1, n2, n3)

	# send one packet
	# p = packet.Packet(destination_address=n1.get_address('n2'),ident=1,protocol='delay',length=1000)
	# Sim.scheduler.add(delay=0, event=p, handler=n3.send_packet)

def prt2():

	n1, n2, n3, net = setupNetwork('./networks/2-2.txt')
	
	queuePackets(1000, n1, n2, n3)

	# send one packet
	#p = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
	#Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

"""
	def prt3():

		n1, n2, net = setupNetwork('./networks/1-3.txt')

		# send three packets at time 0
		p1 = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
		Sim.scheduler.add(delay=0, event=p1, handler=n1.send_packet)

		p2 = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
		Sim.scheduler.add(delay=0, event=p2, handler=n1.send_packet)

		p3 = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
		Sim.scheduler.add(delay=0, event=p3, handler=n1.send_packet)
		# Late packet
		p4 = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
		Sim.scheduler.add(delay=2, event=p4, handler=n1.send_packet)
"""

def queuePackets(count, n1, n2, n3):
	for i in range(count):
		p = packet.Packet(destination_address=n3.get_address('n2'),ident=1,protocol='delay',length=1000)
		Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

if __name__ == '__main__':
	
	# prt1()
	prt2()
	# run the simulation
	Sim.scheduler.run()
