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
        self.broadcast_delay = 30
        self.default_iters = 10
        self.broadcast_iters = self.default_iters
        self.drop_cycles = 3
        self.neighbor_vectors = {}          # map of address to a distance vector (the keyset will be the neighbors)
        self.neighbor_countdown = {}
        self.dist_vector = self.init_dv()   # map of address to distance
        self.forwarding_table = {}          # map of address to link
        self.print_received = False
        self.filter = False
        self.host_to_filter = 'n5'
        self.broadcast()
        # TODO: schedule the first broadcast for right now

    def trace(self,message):
        Sim.trace("DVR",message)

    def reset_cycle(self):
        self.broadcast_iters = self.default_iters
        self.broadcast()

    def receive_packet(self,packet):
        # update the routing table
        # also add forwarding table entries
        # print "In receive_packet for host " + str(self.node.hostname)
        # return
        if self.filter:
            self.print_received = self.host_to_filter == self.node.hostname
        if self.print_received:
            print "==============================="

            print str(self.node.hostname) + " receiving a new dv from address " + str(packet.source_address)
            print "Vector received:  " + str(packet.body)
        self.neighbor_vectors[packet.source_address] = packet.body
        self.neighbor_countdown[packet.source_address] = self.drop_cycles

        changed = self.recompute_tables()
        if changed:
            # schedule a for right now broadcast
            self.broadcast(reschedule=False)
            pass

        self.update_rt()

        if self.print_received:
            print "==============================="

        # if there are changes, broadcast them to neighbors
        # print Sim.scheduler.current_time(),self.node.hostname,packet.ident

    def init_dv(self):
        
        new_dv = {}

        for link in self.node.links:
            address = self.node.get_address(link.endpoint.hostname)
            new_dv[address] = 0

        return new_dv

    def recompute_tables(self):

        new_dv = self.init_dv()
        self.forwarding_table = {}

        for neighbor in self.neighbor_vectors.keys():
            # print neighbor
            # print self.neighbor_vectors[neighbor]

            for address in self.neighbor_vectors[neighbor].keys():

                entry_dist = self.neighbor_vectors[neighbor][address]
                total_dist = entry_dist + self.neighbor_dist(neighbor)

                if (address not in new_dv) or \
                    (total_dist < new_dv[address]):

                    new_dv[address] = total_dist
                    self.forwarding_table[address] = self.neighbor_link(neighbor)

        
        if self.print_received:
            print "DV before update: " + str(self.dist_vector)
            print "DV after update:  " + str(new_dv)

        changed = new_dv != self.dist_vector
        self.dist_vector = new_dv
        return changed       # return True if the table changed somehow

    def neighbor_dist(self,n_address):
        return self.neighbor_link(n_address).weight

    def neighbor_link(self,n_address):
        return self.node.get_rev_link(n_address)

    def update_rt(self):
        
        for entry in self.forwarding_table.keys():
            self.node.add_forwarding_entry(address=entry,link=self.forwarding_table[entry])

    def dec_neighbors(self):

        for neighbor in self.neighbor_countdown.keys():
            current = self.neighbor_countdown[neighbor]
            current -= 1
            if current <= 0:
                del self.neighbor_vectors[neighbor]
                del self.neighbor_countdown[neighbor]
                del self.dist_vector[neighbor]
                del self.forwarding_table[neighbor]
            else:
                self.neighbor_countdown[neighbor] = current

    def broadcast(self,reschedule=True):
        # for each link, send a copy of the routingTable using a packet with protocol "dvr"
        # pass
        # print self.node.hostname
        # self.node.links[0]
        p = packet.Packet(source_address=self.node.links[0].address,destination_address=0,ident=1,ttl=1,protocol='dvr',length=100,body=self.dist_vector)
        Sim.scheduler.add(delay=0, event=p, handler=self.node.send_packet)

        if reschedule and self.broadcast_iters > 0:
            # print self.broadcast_iters
            self.broadcast_iters -= 1
            self.dec_neighbors()
            Sim.scheduler.add(delay=self.broadcast_delay, event=True, handler=self.broadcast)
            # self.trace("Scheduled broadcast for host " + str(self.node.hostname) + " with dv = " + str(self.dist_vector))
        # TODO: schedule this function to happen again in 30 seconds

    def pretty_ft(self):
        result = "{"
        for entry in self.forwarding_table:
            result += str(entry)
            result += ": "
            result += str(self.forwarding_table[entry].address)
            result += ", "
        result = result[:len(result)-2]
        result += "}"
        return result

def run():
    Sim.scheduler.run()
    pass

def trace_on():
    Sim.set_debug("Node")
    Sim.set_debug("Link")

def trace_off():
    Sim.rem_debug("Node")
    Sim.rem_debug("Link")

def sched_down(n1,n2,delay):
    Sim.scheduler.add(delay=delay, event=None, handler=n1.get_link(n2.hostname).down)
    Sim.scheduler.add(delay=delay, event=None, handler=n2.get_link(n1.hostname).down)

def sched_up(n1,n2,delay):
    Sim.scheduler.add(delay=delay, event=None, handler=n1.get_link(n2.hostname).up)
    Sim.scheduler.add(delay=delay, event=None, handler=n2.get_link(n1.hostname).up)

def rebroadcast(apps):
    for i in range(0,len(apps)):
        apps[i].reset_cycle()

def simple_send(nodes,si,sh,di,dh,delay):
    p = packet.Packet(source_address=nodes[si].get_address(sh),destination_address=nodes[di].get_address(dh),ident=1,length=100)
    Sim.scheduler.add(delay=delay, event=p, handler=nodes[si].send_packet)

def get_nodes(location, count):
    net = Network(location)

    nodes = []
    apps = []

    for i in range(1,count+1):
        n = net.get_node('n' + str(i))
        dvr = DVRApp(n)
        nodes.append(n)
        apps.append(dvr)
        n.add_protocol(protocol="dvr",handler=dvr)

    return nodes, apps

def five_node_line_exp():
    nodes, apps = get_nodes('../networks/five-node-line.txt', 5)

    run()

    trace_on()

    simple_send(nodes,0,'n2',4,'n4',0)

    run()

    print_tables(nodes, apps)

def five_node_ring_exp():
    nodes, apps = get_nodes('../networks/five-node-ring.txt', 5)

    run()

    print_tables(nodes,apps)

    trace_on()

    simple_send(nodes,0,'n5',4,'n1',0)

    sched_down(nodes[0],nodes[4], 10)

    run()

    trace_off()

    rebroadcast(apps)

    run()

    print_tables(nodes,apps)

    trace_on()

    simple_send(nodes,0,'n5',4,'n1',0)

    run()


def fifteen_nodes_exp():

    nodes, apps = get_nodes('../networks/fifteen-nodes.txt', 15)

    run()
    
    trace_on()
    
    simple_send(nodes,0,'n4',11,'n5',0)
    # p = packet.Packet(source_address=nodes[0].get_address('n4'),destination_address=nodes[11].get_address('n5'),ident=1,length=100)
    # Sim.scheduler.add(delay=0, event=p, handler=nodes[0].send_packet)

    sched_down(nodes[4],nodes[3],10)

    run()

    trace_off()

    rebroadcast(apps)

    run()

    trace_on()
    
    simple_send(nodes,0,'n4',11,'n5',0)
    # p = packet.Packet(source_address=nodes[0].get_address('n4'),destination_address=nodes[11].get_address('n5'),ident=1,length=100)
    # Sim.scheduler.add(delay=0, event=p, handler=nodes[0].send_packet)

    sched_up(nodes[4],nodes[3],10)

    run()

    trace_off()

    rebroadcast(apps)

    run()

    trace_on()

    simple_send(nodes,0,'n4',11,'n5',0)
    # p = packet.Packet(source_address=nodes[0].get_address('n4'),destination_address=nodes[11].get_address('n5'),ident=1,length=100)
    # Sim.scheduler.add(delay=0, event=p, handler=nodes[0].send_packet)

    run()

def print_tables(nodes, apps):
    print "==============================="
    for i in range(0,len(nodes)):
        print "Final DV for " + str(nodes[i].hostname) + ": " + str(apps[i].dist_vector)

    print "==============================="

    for i in range(0,len(nodes)):
        print "Final forwarding table for " + str(nodes[i].hostname) + ": " + str(apps[i].pretty_ft())


if __name__ == '__main__':
    
    Sim.scheduler.reset()
    Sim.set_debug("DVR")

    # five_node_line_exp()
    five_node_ring_exp()
    # fifteen_nodes_exp()
