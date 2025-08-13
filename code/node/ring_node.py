from node.node import Node
from msg.ring_msg import CoordinatorRingMsg, ElectionRingMsg

import utils

# this class represents a node in the ring algorithm execution
class RingNode(Node):

    def __init__(self, env, id, delay_mean):
       super().__init__(env, id)
       self.initiator = False
       self.delay_mean = delay_mean
       self.participant = False
       
       self.env.process(self.receive())

    def initiate(self):
        self.initiator = True

        # DEBUG
        print(f"Time {self.env.now:.2f}: Node {self.id} initiates an election")

    def send(self, msg):

        # message delay -> must be modified with exponential delays
        yield self.env.timeout(utils.delay(self.delay_mean))

        # find the next active neighbor
        next = self.find_neighbor()
        yield self.peers[next].queue.put(msg) 
        #self.env.process(self.peers[next].receive())

        # DEBUG
        if msg.type == "ELECTION":
            print(f"Time {self.env.now:.2f}: Node {self.id} sends {msg.type} with IDs {msg.ids} to node {next}")
        elif msg.type == "COORDINATOR":
            print(f"Time {self.env.now:.2f}: Node {self.id} sends {msg.type} with ID {msg.elected} to node {next}")


    def receive(self):
        # OBS: the get waits until there is something in the store
        while True:
            msg = yield self.queue.get()
            if msg.type == "ELECTION":
                if self.id in msg.ids:
                    leader = max(msg.ids)
                    self.elected = leader
                    self.env.process(self.send(CoordinatorRingMsg(self.id, leader)))
                else:
                    self.participant = True
                    msg.ids.append(self.id)
                    self.env.process(self.send(ElectionRingMsg(msg.ids)))
            elif msg.type == "COORDINATOR":
                if self.id != msg.initiator:
                    self.elected = msg.elected
                    self.env.process(self.send(CoordinatorRingMsg(msg.initiator, msg.elected)))
            

    # find the next active neighbor
    def find_neighbor(self):
        for i in range(1,len(self.peers)):
            next = self.peers[(i+self.id)%len(self.peers)];
            if next.crashed == False:
                return next.id