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

        # send window; represents the total number of bytes that may
        # be outstanding at one time
        # Step 2
        self.window = window
        # send buffer
        self.send_buffer = SendBuffer()
        # maximum segment size, in bytes
        # self.mss = 1000
        self.mss = min(1000, window)
        # largest sequence number that has been ACKed so far; represents
        # the next sequence number the client expects to receive
        self.sequence = 0
        # retransmission timer
        self.timer = None
        # timeout duration in seconds
        self.timeout = 3.0
        # estimated rtt
        self.est_rtt = None
        # alpha
        self.alpha = 0.125
        # variation rtt
        self.var_rtt = None  ## TODO: revisit this later
        # beta
        self.beta = 0.25
        # timer start
        self.start_time = 0.0
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

    ''' Sender '''

    ''' Send data on the connection. Called by the application. This
        code currently sends all data immediately. '''
    ''' 1 '''
    def send(self,data):
        # Step 1
        print "received data of size:" + str(len(data))
        self.send_buffer.put(data)
        self.send_max()
        

    def send_max(self):
        # Step 3
        while (self.send_buffer.next - self.send_buffer.base) < self.window \
            and (self.send_buffer.last - self.send_buffer.next) > 0:

            dataSize = min((self.window - (self.send_buffer.next - self.send_buffer.base)), self.mss)
            dataToSend, sequenceToSend = self.send_buffer.get(dataSize)
            # print "sending this data: " + str(dataToSend)
            # print "the sequence of that data :" + str(sequenceToSend)
            # print "the size of that data :" + str(len(dataToSend))

            print "send buffer next: " +  str(self.send_buffer.next)
            print "send buffer base: " +  str(self.send_buffer.base)

            self.send_packet(dataToSend, sequenceToSend)
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
        self.trace("%s (%d) sending TCP segment to %d for %d" % (self.node.hostname,self.source_address,self.destination_address,packet.sequence))
        self.transport.send_packet(packet)
        # Step 4
        # set a timer
        if not self.timer:
            self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)
            self.start_time = Sim.scheduler.current_time()

    def handle_ack(self,packet):
        ''' Handle an incoming ACK. '''
        ''' Do elements 5, 6, and 7 '''
        ''' Also adjust the timer somewhere...'''
        print "About to check ack_number > sequence: " + str(packet.ack_number) + " ? " + str(self.sequence)
        if packet.ack_number > self.sequence:

            sample_rtt = Sim.scheduler.current_time() - packet.time_stamp
            self.cancel_timer()
            self.adjust_timeout(sample_rtt)

            self.sequence = packet.ack_number
            print "Handling Ack with an ack number of: " + str(packet.ack_number)
            if not self.send_buffer.slide(self.sequence):
                self.cancel_timer()
            print "After handling the ack, our buffer base is " + str(self.send_buffer.base) + " and next is " + str(self.send_buffer.next)
            self.send_max()


    def retransmit(self,event):
        ''' Retransmit data. '''
        ''' 8 and 9 '''
        self.timer = None
        dataToRetransmit, sequenceToRetransmit = self.send_buffer.resend(self.mss)
        self.send_packet(dataToRetransmit, sequenceToRetransmit)
        self.trace("%s (%d) retransmission timer fired" % (self.node.hostname,self.source_address))

    def cancel_timer(self):
        ''' Cancel the timer. '''
        if not self.timer:
            return
        Sim.scheduler.cancel(self.timer)
        self.timer = None

    ''' Receiver '''

    def handle_data(self,packet):
        ''' Handle incoming data. This code currently gives all data to
            the application, regardless of whether it is in order, and sends
            an ACK.'''
        ''' R1 '''
        self.trace("%s (%d) received TCP segment from %d for %d" % (self.node.hostname,packet.destination_address,packet.source_address,packet.sequence))
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
        self.trace("%s (%d) sending TCP ACK to %d for %d" % (self.node.hostname,self.source_address,self.destination_address,packet.ack_number))
        self.transport.send_packet(packet)

    def adjust_timeout(self,sample_rtt):
        if not self.est_rtt:
            self.est_rtt = sample_rtt
        else:
            self.est_rtt = ((1 - self.alpha) * self.est_rtt) + (self.alpha * sample_rtt)
        if not self.var_rtt:
            self.var_rtt = sample_rtt/2
        else:
            self.var_rtt = ((1 - self.beta) * self.var_rtt) + (self.beta * abs(sample_rtt - self.est_rtt))

        self.timeout = self.est_rtt + max(1.0, 4.0*self.var_rtt)


