from numpy import random
from node.node import Node
from msg.bully_msg import BullyMsg
from utils import delay
from scipy.stats import expon
from simpy.core import StopSimulation

# this class represents a node in the bully algorithm execution
class BullyNode(Node):

    def __init__(self, env, id, delay_mean):
        super().__init__(env, id)
        self.elected = -1
        self.el_in_progress = False
        self.blocked = False
        self.missing_ack = []
        #   maximum wait is computed using quantiles
        self.max_wait = expon.ppf(0.8, loc = 0, scale = delay_mean)
        self.delay_mean = delay_mean


    def reliable_send(self, type, dest_id):
        
        if not self.peers[dest_id].crashed:
            # create the election message
            election_msg = BullyMsg(type, self.id)

            # DEBUG
            print(f"Time {self.env.now:.2f}: Node {self.id} sends {type} to node {dest_id}")

            yield self.env.timeout(delay(self.delay_mean))
            # send the message
            yield self.peers[dest_id].queue.put(election_msg)
            self.env.process(self.peers[dest_id].reliable_receive())

    def reliable_receive(self):
        
        msg = yield self.queue.get()
        if msg.type == "ELECTION":
            if msg.sender_id == -1:
                # start election
                print(f"\033[94mTime {self.env.now:.2f}: Node {self.id} detected coordinator crash\033[0m")
            else:
                # DEBUG
                print(
                    f"Time {self.env.now:.2f}: Node {self.id} receives ELECTION message from node {msg.sender_id}"
                )

            if self.id > msg.sender_id:
                if msg.sender_id != -1:
                    # if id is greater than sender: stop election
                    self.env.process(self.reliable_send("OK", msg.sender_id))
                if not self.el_in_progress:
                    # each node can only start election ONCE
                    self.el_in_progress = True
                    # send ELECTION messages to all nodes with greater id
                    for i in range(self.id + 1, len(self.peers)):
                        self.env.process(self.reliable_send("ELECTION", i))
                    
                    # wait for max delay
                    yield self.env.timeout(2 * self.max_wait * (len(self.peers) - self.id - 1))

                    # wait for a certain time to be passed ... if it wasn't stopped it is elected
                    if not self.blocked:
                        for i in range(len(self.peers)):
                            self.env.process(
                                self.reliable_send("COORDINATOR", self.peers[i].id))
                    # election of node ended
                    self.el_in_progress = False

        elif msg.type == "OK":
            # DEBUG
            print(
                f"Time {self.env.now:.2f}: Node {self.id} receives OK message from node {msg.sender_id}"
            )
            # stop election
            self.blocked = True

        elif msg.type == "COORDINATOR":
            # DEBUG
            print(f"\033[92mTime {self.env.now:.2f}: Node {self.id} elects {msg.sender_id} as coordinator\033[0m")
            self.elected = msg.sender_id
            # if active, set election status of node
            self.el_in_progress = False
            # if election terminated trigger finish event
            if self.finished():
                self.finish.succeed()
                raise StopSimulation("Election finished")

    # UNRELIABLE SEND/RECEIVE FUNCTIONS ---------------------------------------------------------------------------
    
    def unreliable_send(self, type, dest_id):
        
        if not self.peers[dest_id].crashed:
            # create the election message
            election_msg = BullyMsg(type, self.id)

            # DEBUG
            print(f"Time {self.env.now:.2f}: Node {self.id} sends {type} to node {dest_id}")

            # is packet lost?
            if random.uniform(0, 1) > self.loss_rate:
                yield self.env.timeout(delay(self.delay_mean))
                # send the message
                yield self.peers[dest_id].queue.put(election_msg)
                self.env.process(self.peers[dest_id].unreliable_receive())
            else:
                # DEBUG
                print(f"\033[31mTime {self.env.now:.2f}: Lost {type} message from node {self.id} to node {dest_id}\033[0m")
       

    def unreliable_receive(self):
        
        msg = yield self.queue.get()
        if msg.type == "ELECTION":
            if msg.sender_id == -1:
                # start election
                print(f"\033[94mTime {self.env.now:.2f}: Node {self.id} detected coordinator crash\033[0m")
            else:
                # DEBUG
                print(
                    f"Time {self.env.now:.2f}: Node {self.id} receives ELECTION message from node {msg.sender_id}"
                )

            if self.id > msg.sender_id:
                if msg.sender_id != -1:
                    # if id is greater than sender: stop election
                    self.env.process(self.unreliable_send("OK", msg.sender_id))

                if not self.el_in_progress:
                    # each node can only start election ONCE
                    self.el_in_progress = True
                    # send ELECTION messages to all nodes with greater id
                    self.missing_ack.extend(range(self.id + 1, len(self.peers) - 1))
                    
                    while self.el_in_progress:
                        for n_id in self.missing_ack:
                            self.env.process(self.unreliable_send("ELECTION", n_id))
                            
                        # delay is computed as 2 * max_RTT * number of receivers
                        yield self.env.timeout(2 * self.max_wait * len(self.missing_ack) )
                        # timeout triggered check responses
                        if not self.blocked:
                            # no OK received, check how many answer were received
                            if len(self.missing_ack) == 0:
                                # not waiting for any response: this node is the one with highest id
                                # prepare to wait for all nodes to send ACK of COORDINATOR message
                                self.missing_ack = []
                                self.missing_ack.extend(range(0, len(self.peers) - 1))
                                # do not send COORDINATOR message to self
                                self.missing_ack.remove(self.id)

                                while len(self.missing_ack) != 0:
                                    for n_id in self.missing_ack:
                                        self.env.process(self.unreliable_send("COORDINATOR", n_id))
                                    # set timeout for retransmission
                                    yield self.env.timeout(2 * self.max_wait * len(self.missing_ack) )
                                
                                # election of group terminated trigger finish event
                                self.elected = self.id
                                self.finish.succeed()
                                raise StopSimulation("Election finished")

                        else:
                            # there is another node with higher id
                            self.el_in_progress = False    
            else:    
                self.env.process(self.unreliable_send("ACK", msg.sender_id))               


        elif msg.type == "OK":
            # DEBUG
            print(
                f"Time {self.env.now:.2f}: Node {self.id} receives OK message from node {msg.sender_id}"
            )
            # stop election
            self.blocked = True

        elif msg.type == "ACK":
            # DEBUG
            print(
                f"Time {self.env.now:.2f}: Node {self.id} receives ACK message from node {msg.sender_id}"
            )
            # remove from the node from missing_ack list
            if msg.sender_id in self.missing_ack:
                # you could receive an ack twice
                self.missing_ack.remove(msg.sender_id)

        elif msg.type == "COORDINATOR":
            # DEBUG
            print(f"\033[92mTime {self.env.now:.2f}: Node {self.id} elects {msg.sender_id} as coordinator\033[0m")
            # send ACK
            self.env.process(self.unreliable_send("ACK", msg.sender_id))
            self.elected = msg.sender_id
            
            # if active, set election status of node
            self.el_in_progress = False


    # returns True if all nodes decided on coordinator
    def finished(self):
        for i in range(len(self.peers)):
            if self.peers[i].elected == -1 and not self.peers[i].crashed:  # count only non crashed processes
                return False
        return True

    # resets node to default status
    def reset(self):
        self.blocked = False
        self.crashed = False
        self.elected = -1
        self.el_in_progress = False
        self.missing_ack = []
    
    # sets wether election happens with reliable or unreliable links with a network packet loss rate
    def set_behaviour(self, loss_rate):
        self.loss_rate = loss_rate
