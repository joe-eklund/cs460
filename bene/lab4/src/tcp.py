import sys

from sim import Sim
from connection import Connection
from tcppacket import TCPPacket
from buffer import SendBuffer,ReceiveBuffer

class TCP(Connection):
    ''' A TCP connection between two hosts.'''
    def __init__(self,transport,source_address,source_port,
                 destination_address,destination_port,app=None,window=1000):
        Connection.__init__(self,transport,source_address,source_port,
                            destination_address,destination_port,app)

        ### Sender functionality
        self.totalQueueingDelay = 0.0
        self.totalPacketsSent = 0
        self.port = source_port
        self.dynamic = True
        self.output = False
        self.proveTimer = False
        self.proveCong = False
        self.stand_trace = False
        self.seq_plot = False
        self.graph1 = False
        self.graph2 = False     # == This is controlled in the transfer file by Sim.set_debug('Link')
        self.graph3 = False
        self.graph4 = True

        if self.graph2:
            Sim.set_debug('Link')
        # send window; represents the total number of bytes that may
        # be outstanding at one time
        # maximum segment size, in bytes
        self.mss = 1000
        # Step 2
        self.window = self.mss  ######################### This one gets the mess adjusted out of it
        # threshold for slow start
        self.thresh = 500000
        self.inc_sum = 0
        # for fast retransmit
        self.last_ack = 0
        self.dup_counter = 0
        self.drop_next = False
        self.has_dropped = False
        self.dropped_count = 0
        # send buffer
        self.send_buffer = SendBuffer()
        ############################################# (this never gets adjusted)
        #self.mss = min(1000, window) ################ TODO: handle the case where window is bigger than mss
        # largest sequence number that has been ACKed so far; represents
        # the next sequence number the client expects to receive
        self.sequence = 0
        # retransmission timer
        self.timer = None
        # timeout duration in seconds
        self.timeout = 1.0
        if self.dynamic:
            self.timeout = 3.0
        # estimated rtt
        self.est_rtt = None
        # alpha
        self.alpha = 0.125
        # variation rtt
        self.var_rtt = None  ## TODO: revisit this later
        # beta
        self.beta = 0.25
        ### Receiver functionality

        # receive buffer
        self.receive_buffer = ReceiveBuffer()
        # ack number to send; represents the largest in-order sequence
        # number not yet received
        self.ack = 0

    def trace(self,message):
        ''' Print debugging messages. '''
        Sim.trace("TCP",message)

    def receive_packet(self,packet):
        ''' Receive a packet from the network layer. '''
        if packet.ack_number > 0:
            # handle ACK
            self.handle_ack(packet)
        if packet.length > 0:
            # handle data
            self.handle_data(packet)
            self.totalQueueingDelay += packet.queueing_delay

    ''' Sender '''

    ''' Send data on the connection. Called by the application. This
        code currently sends all data immediately. '''
    ''' 1 '''
    def send(self,data):
        # Step 1
        if self.output:
            print "received data of size:" + str(len(data))
        self.send_buffer.put(data)
        self.send_max()
        

    def send_max(self):
        # Step 3
        while (self.send_buffer.next - self.send_buffer.base) < self.window \
            and (self.send_buffer.last - self.send_buffer.next) > 0:

            dataSize = min((self.window - (self.send_buffer.next - self.send_buffer.base)), self.mss)
            dataToSend, sequenceToSend = self.send_buffer.get(dataSize)
            if self.output:
                # print "sending this data: " + str(dataToSend)
                # print "the sequence of that data :" + str(sequenceToSend)
                # print "the size of that data :" + str(len(dataToSend))

                print "send buffer next: " +  str(self.send_buffer.next)
                print "send buffer base: " +  str(self.send_buffer.base)

            self.send_packet(dataToSend, sequenceToSend)

        if self.output:
            print "breaking out of the loop"

    def send_packet(self,data,sequence):
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           body=data,
                           sequence=sequence,ack_number=self.ack,
                           time_stamp=Sim.scheduler.current_time())

        # send the packet
        if self.stand_trace:
            self.trace("%s (%d) sending TCP segment to %d for %d" % (self.node.hostname,self.source_address,self.destination_address,packet.sequence))
        if self.seq_plot:
            self.trace("%d T" % (packet.sequence))
        if self.graph4:
            self.trace(str(self.port) + " " + str(packet.sequence) + " T")

        self.transport.send_packet(packet)

        # Step 4
        # set a timer
        if not self.timer:
            if self.proveTimer:
                print "Starting timer with timeout of: " + str(self.timeout)
            self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)

    def handle_ack(self,packet):
        ''' Handle an incoming ACK. '''
        ''' Do elements 5, 6, and 7 '''
        ''' Also adjust the timer somewhere...'''
        if self.output:
            print "About to check ack_number > sequence: " + str(packet.ack_number) + " ? " + str(self.sequence)
        if self.seq_plot:
            self.trace("%d A" % (packet.ack_number))
        if self.graph4:
            self.trace(str(self.port) + " " + str(packet.ack_number) + " A")

        # handle duplicate acks
        if packet.ack_number == self.last_ack:
            if self.seq_plot:
                self.trace("%d A" % (packet.ack_number))
            if self.graph4:
                self.trace(str(self.port) + " " + str(packet.ack_number) + " A")
            if self.proveCong:
                print "We have 1 duplicate of " + str(self.last_ack)
            self.dup_counter += 1
            if self.dup_counter == 3:
                if self.proveCong:
                    print "We have 3 duplicate ACKs"
                self.cancel_timer()
                self.retransmit('3_dups')

        # handle new data
        if packet.ack_number > self.sequence:   # we have received new data
            self.last_ack = packet.ack_number
            self.dup_counter = 0
            # dynamic retransmission timer
            sample_rtt = Sim.scheduler.current_time() - packet.time_stamp
            self.restart_timer()
            if self.dynamic:
                self.adjust_timeout(sample_rtt)

            # adjusting the window for slow start
            newBytes = packet.ack_number - self.sequence
            if self.proveCong:
                print "\nWT: Window: " + str(self.window) + "  Threshold: " + str(self.thresh)

            if self.window < self.thresh:   # exponential increase
                if self.proveCong:
                    print "EI: setting window to " + str(self.window) + " += " + str(packet.ack_number) + " - " + str(self.sequence)
                self.window += self.mss
                if self.graph3:
                    self.trace(str(self.port) + " " + str(self.window))
            else:                           # additive increase
                #"""
                self.inc_sum += (self.mss * newBytes) / self.window     # gather increase until > mss
                mss_count = int(self.inc_sum / self.mss)                # how many mss's do we have
                self.inc_sum = self.inc_sum % self.mss                  # how much is left over (save that)
                if self.proveCong:
                    print "AI: setting window to " + str(self.window) + " += " + str(self.mss) + " * " + str(mss_count)
                    print "AI: remaining inc_sum is " + str(self.inc_sum)
                self.window += self.mss * mss_count                     # adjust window
                if self.graph3:
                    self.trace(str(self.port) + " " + str(self.window))

            # == UNCOMMENT THIS FOR DROPPING 3 PACKETS (as well as the code around line 130)
            # if self.window == 28000:
            #     self.drop_next = True


            # normal ack handling
            self.sequence = packet.ack_number
            if self.output:
                print "Handling Ack with an ack number of: " + str(packet.ack_number)
            if not self.send_buffer.slide(self.sequence):
                self.cancel_timer()
            if self.output:
                print "After handling the ack, our buffer base is " + str(self.send_buffer.base) + " and next is " + str(self.send_buffer.next)
            self.send_max()


    def retransmit(self,event):
        ''' Retransmit data. '''
        ''' 8 and 9 '''
        self.timer = None
        #print str(event)
        if self.dynamic:    # dynamic retransmission timer
            self.timeout *= 2
            if self.proveTimer:
                print "**Timer expired. Doubled timeout to " + str(self.timeout)

        # multiplicative decrease
        self.thresh = int(max(self.window/2, self.mss))
        self.window = self.mss
        if self.graph3:
            self.trace(str(self.port) + " " + str(self.window))
        self.inc_sum = 0

        # actually retransmit
        dataToRetransmit, sequenceToRetransmit = self.send_buffer.resend(self.mss)

        if self.seq_plot:
            self.trace("%d X" % (sequenceToRetransmit))
        if self.graph4:
            self.trace(str(self.port) + " " + str(sequenceToRetransmit) + " X")

        self.send_packet(dataToRetransmit, sequenceToRetransmit)

        if self.stand_trace:
            self.trace("%s (%d) retransmission timer fired" % (self.node.hostname,self.source_address))

    def cancel_timer(self):
        ''' Cancel the timer. '''
        if not self.timer:
            return
        Sim.scheduler.cancel(self.timer)
        self.timer = None

    def restart_timer(self):
        self.cancel_timer()
        self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)

    ''' Receiver '''

    def handle_data(self,packet):
        ''' Handle incoming data. This code currently gives all data to
            the application, regardless of whether it is in order, and sends
            an ACK.'''
        ''' R1 '''
        if self.stand_trace:
            self.trace("%s (%d) received TCP segment from %d for %d" % (self.node.hostname,packet.destination_address,packet.source_address,packet.sequence))
        if self.graph1:
            self.trace(str(self.port))#"%d" % (packet.sequence))
        self.receive_buffer.put(packet.body,packet.sequence)
        data, start = self.receive_buffer.get()
        self.ack = start + len(data)
        self.app.receive_data(data)
        #old self.app.receive_data(packet.body)
        self.send_ack(packet.time_stamp)

    def send_ack(self, time_stamp):
        ''' Send an ack. '''
        ''' R2 '''
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           sequence=self.sequence,ack_number=self.ack,
                           time_stamp=time_stamp)
        # send the packet
        if self.stand_trace:
            self.trace("%s (%d) sending TCP ACK to %d for %d" % (self.node.hostname,self.source_address,self.destination_address,packet.ack_number))
        self.transport.send_packet(packet)

    def adjust_timeout(self,sample_rtt):
        if self.proveTimer:
            print "Received ACK with RTT of: " + str(sample_rtt)
        if not self.est_rtt:
            self.est_rtt = sample_rtt
        else:
            self.est_rtt = ((1 - self.alpha) * self.est_rtt) + (self.alpha * sample_rtt)
        if not self.var_rtt:
            self.var_rtt = sample_rtt/2
        else:
            self.var_rtt = ((1 - self.beta) * self.var_rtt) + (self.beta * abs(sample_rtt - self.est_rtt))
        before = self.timeout

        self.timeout = self.est_rtt + max(1.0, 4.0*self.var_rtt)
        if self.proveTimer:
            print "Timeout adjusted from " + str(before) + " to " + str(self.timeout)

