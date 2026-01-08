from numpy import random

from node.node import Node
from msg.ring_msg import CoordinatorRingMsg, ElectionRingMsg, RingMsg

import utils

# this class represents a node in the ring algorithm execution
#   attributes:
#       env - simpy env
#       id - id of the node
#       delay_mean - exponential mean for setting propagation delays  
#       unreliable - boolean value, if true we use replication to tolerate unreliable links  
#       debug_mode - if true the nodes and this class will print debug messages
#       loss - loss rate of packets (unreliable)
#       timeout - max timeout to wait (unreliable)
#       rng - random number generator
#       id_stats - unique id of the execution for the SimStats of the simulation
#       sim_stats - reference to the SimStats of the simulation
class RingNode(Node):

    def __init__(self, env, id, delay_mean, unreliable, debug_mode, loss, timeout,
                    rng, id_stats, sim_stats):
       super().__init__(env, id, delay_mean)
       self.unreliable = unreliable
       self.debug_mode=debug_mode           # debug
       self.loss=loss
       self.timeout=timeout
       self.crashed=False
       self.initiator=False
       self.rng = rng           # debug
       self.id_stats = id_stats
       self.sim_stats = sim_stats
       
       self.env.process(self.receive())     # the node can receive and manage messages

    # this method set the initiator parameter to true
    def initiate(self):

        self.initiator=True
        
        if self.debug_mode:
            print(f"Time {self.env.now:.2f}: Node {self.id} initiates an election")

    # this method send an election or a coordinator message to its next active neighbor
    #   params:
    #       msg - message to be sent
    def send(self, msg):

        # we continue sending the message if we didn't receive an ack or there are 
        # reliable links
        while True:

            if self.unreliable: msg.set_event(self.env.event())         # set event for ack        
            delay = utils.delay(self.delay_mean, rng=self.rng)     
            self.sim_stats.add_msg(self.id_stats, delay)
            yield self.env.timeout(delay)       # delay wait time
            next = self.find_next()     # find the next active neighbor
            yield self.peers[next].queue.put(msg)       # send the message 

            if self.debug_mode:
                if msg.type == "ELECTION":
                    print(f"Time {(self.env.now-delay):.2f}: Node {self.id} sends {msg.type} with IDs {msg.ids} to node {next}")
                elif msg.type == "COORDINATOR":
                    print(f"Time {(self.env.now-delay):.2f}: Node {self.id} sends {msg.type} with ID {msg.elected} to node {next}")

            if not self.unreliable: break   # if we have reliable links we do not need acks (replication)

            result = yield self.env.any_of([msg.ack_event, self.env.timeout(self.timeout)])      # wait for the ACK or the timeout
            if msg.ack_event in result:         # the sender received the ack
                break
            else:           # don't stop, restart cycle for resending the message
                if self.debug_mode:
                    print(f"Time {(self.env.now-delay):.2f}: Node {self.id} didn't received ACK_{msg.type} from {next}, resend message")

    # this method is used to send an ack
    #   params:
    #       msg - ack message to be sent
    #       receiver - id of the node that needs to receive the ack
    def send_ack(self, msg, receiver):

        if self.debug_mode: 
            print(f"Time {self.env.now:.2f}: Node {self.id} sends {msg.type} to node {receiver}")
        
        delay = utils.delay(self.delay_mean, rng=self.rng)
        self.sim_stats.add_msg(self.id_stats, delay)
        yield self.env.timeout(delay)       # delay wait time
        yield self.peers[receiver].queue.put(msg)       # send the ack

    # this method is used to manage incoming messages
    def receive(self):
        
        while not self.crashed:
            msg = yield self.queue.get()        # the get waits until there is something in the store

            if self.unreliable and random.uniform(0,1) < self.loss and msg.sender!=-1:    # unreliable links packet losses
                continue      

            if self.debug_mode:
                print(f"Time {self.env.now:.2f}: Node {self.id} receives {msg.type} from node {msg.sender}")

            if msg.type == "ELECTION":
                if self.id in msg.ids:      # the election message performed a cycle
                    leader = max(msg.ids)       # select the new coordinator
                    self.elected = leader
                    self.env.process(self.send(CoordinatorRingMsg(msg.transaction_id,
                                                                    self.id, self.id, leader)))
                else:       # the node receives an election message
                    msg.ids.append(self.id)
                    self.env.process(self.send(ElectionRingMsg(msg.transaction_id,self.id, msg.ids)))

                if self.unreliable and msg.sender!=-1:      # if the node isn't the initiator, send an ACK to the sender
                    self.env.process(self.send_ack(RingMsg("ACK_ELECTION",msg.transaction_id,
                                                            self.id, msg.ack_event), msg.sender))

            elif msg.type == "COORDINATOR":

                if self.id != msg.initiator:        
                    if self.unreliable: 
                        self.env.process(self.send_ack(RingMsg("ACK_COORDINATOR",
                                                                msg.transaction_id,self.id, msg.ack_event) , msg.sender))
                    self.elected = msg.elected
                    self.env.process(self.send(CoordinatorRingMsg(msg.transaction_id, 
                                                                   self.id, msg.initiator, msg.elected)))
                else:           # we finish the simulation when a coordinator cycle is completed
                    self.finish.succeed()       

            elif "ACK" in msg.type:     # we received the ack, we trigger the ack event 
                msg.ack_event.succeed()
            

    # find the next active neighbor
    def find_next(self):
        for i in range(1,len(self.peers)):
            next = self.peers[(i+self.id)%len(self.peers)];
            if next.crashed == False:
                return next.id