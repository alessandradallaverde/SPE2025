from numpy import random
from node.node import Node
from msg.bully_msg import BullyMsg
from utils import delay, max_delay
from simpy import Store, core, AnyOf

# this class represents a node in the bully algorithm execution
class BullyNode(Node):

    def __init__(self, env, id, sim_stats, sim_id, delay_mean, delay_q):
        super().__init__(env, id, delay_mean)
        self.elected = -1
        self.el_in_progress = False
        self.blocked = False
        self.missing_ack = []
        #   maximum wait is computed using the quantile given by delay_q (saved as attribute to reduce calls to scipy)
        self.max_wait = max_delay(delay_q, delay_mean)
        # reference to sim_stat class to record all statistics during simulation
        self.sim_stats = sim_stats
        self.sim_id = sim_id

    def reliable_send(self, type, dest_id):
        
        if not self.peers[dest_id].crashed:
            # create the election message
            election_msg = BullyMsg(type, self.id)

            if self.debug_mode:
                print(f"Time {self.env.now:.2f}: Node {self.id} sends {type} to node {dest_id}")

            # increase message counter
            msg_delay = delay(self.delay_mean)
            self.sim_stats.add_msg(self.sim_id, msg_delay)
            yield self.env.timeout(msg_delay)
            # send the message
            yield self.peers[dest_id].queue.put(election_msg)
            self.env.process(self.peers[dest_id].reliable_receive())

    def reliable_receive(self):
        
        msg = yield self.queue.get()
        if msg.type == "ELECTION":
            
            if self.debug_mode:
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

                    yield self.env.timeout(2 * self.max_wait)

                    # wait for a certain time to be passed ... if it wasn't stopped it is elected
                    if not self.blocked:
                        for i in range(len(self.peers)):
                            self.env.process(
                                self.reliable_send("COORDINATOR", self.peers[i].id))
                    # election of node ended
                    self.el_in_progress = False

        elif msg.type == "OK":
            if self.debug_mode:
                print(
                    f"Time {self.env.now:.2f}: Node {self.id} receives OK message from node {msg.sender_id}"
                )

            # stop election
            self.blocked = True

        elif msg.type == "COORDINATOR":
            if self.debug_mode:
                print(f"\033[92mTime {self.env.now:.2f}: Node {self.id} elects {msg.sender_id} as coordinator\033[0m")
            
            self.elected = msg.sender_id
            # if active, set election status of node
            self.el_in_progress = False
            # if election terminated trigger finish event
            is_finished, electee = self.finished()
            if is_finished:
                # set value of event
                self.finish.succeed(electee)
                raise core.StopSimulation("")

    # UNRELIABLE SEND/RECEIVE FUNCTIONS ---------------------------------------------------------------------------
    
    def unreliable_send(self, type, dest_id):
        
        if not self.peers[dest_id].crashed:
            # create the election message
            election_msg = BullyMsg(type, self.id)
            
            if self.debug_mode:
                print(f"Time {self.env.now:.2f}: Node {self.id} sends {type} to node {dest_id}")

            # is packet lost?
            if random.uniform(0, 1) > self.loss_rate:
                # increase message counter
                msg_delay = delay(self.delay_mean)
                self.sim_stats.add_msg(self.sim_id, msg_delay)
                yield self.env.timeout(msg_delay)
                # send the message
                yield self.peers[dest_id].queue.put(election_msg)
                self.env.process(self.peers[dest_id].unreliable_receive())
            elif self.debug_mode:
                # DEBUG
                print(f"\033[31mTime {self.env.now:.2f}: Lost {type} message from node {self.id} to node {dest_id}\033[0m")
       

    def unreliable_receive(self):
        msg = yield self.queue.get()
        # keep track of highest node id that ever interacted with this node
        self.max_active_id = max(self.max_active_id, msg.sender_id)
        if msg.type == "ELECTION":
            if self.debug_mode:
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

                # OPTIMIZATION: don't even start election if you already know of a node with higher ID
                if (not self.el_in_progress) and self.max_active_id <= self.id:
                    # each node can only start election ONCE (retransmissions are not counted)
                    self.el_in_progress = True
                    # send ELECTION messages to all nodes with greater id
                    self.missing_ack = []
                    self.missing_ack.extend(range(self.id + 1, len(self.peers) - 1))
                    yield self.env.process(self.retransmit("ELECTION"))
                    
                    # all answers recived: proceed
                    if not self.blocked:
                        # no OK received: this node is the one with highest id
                        # prepare to wait for all nodes to send ACK of COORDINATOR message
                        self.missing_ack = []
                        self.missing_ack.extend(range(0, len(self.peers) - 1))
                        # do not send COORDINATOR message to self
                        self.missing_ack.remove(self.id)
                        yield self.env.process(self.retransmit("COORDINATOR"))
                        # election of group terminated trigger finish event
                        self.elected = self.id
                        self.finish.succeed(self.id)
                        raise core.StopSimulation("") 

            else:    
                self.env.process(self.unreliable_send("ACK", msg.sender_id))               


        elif msg.type == "OK":
            if self.debug_mode:
                print(
                    f"Time {self.env.now:.2f}: Node {self.id} receives OK message from node {msg.sender_id}"
                )
            
            self.update_ack_list(msg.sender_id)
            # stop election
            self.blocked = True

        elif msg.type == "ACK":
            if self.debug_mode:
                print(
                    f"Time {self.env.now:.2f}: Node {self.id} receives ACK message from node {msg.sender_id}"
                )
            
            self.update_ack_list(msg.sender_id)

        elif msg.type == "COORDINATOR":
            if self.debug_mode:
                print(f"\033[92mTime {self.env.now:.2f}: Node {self.id} elects {msg.sender_id} as coordinator\033[0m")
            
            # send ACK
            self.env.process(self.unreliable_send("ACK", msg.sender_id))
            self.elected = msg.sender_id
            
            # if active, set election status of node
            self.el_in_progress = False

    # udpates ack list counter and triggers appropriate event when all answers arrived
    def update_ack_list(self, sender): 
        # remove the node from missing_ack list
        if sender in self.missing_ack:
            # you could receive an ack/OK twice
            self.missing_ack.remove(sender)

        if len(self.missing_ack) == 0 and not self.wait_msg.triggered:
            # trigger event
            self.wait_msg.succeed()
    
    # send message that will be retransmitted if not all answers are received
    def retransmit(self, msg_type):
        self.wait_msg = self.env.event()
        # OPTIMIZATION
        # If while retransmitting a message you discover a node of higher ID quit
        while len(self.missing_ack) != 0 and not self.blocked:
            for n_id in self.missing_ack:
                self.env.process(self.unreliable_send(msg_type, n_id))
            # set timeout /wait for anwers
            yield AnyOf(self.env, [self.wait_msg, self.env.timeout(2 * self.max_wait)])

    # returns array with two values:
    # - first: is True if all nodes decided on coordinator
    # - second: is an integer (-1 = different coordinators, otherwise it indicates the node that was elected)
    def finished(self):
        electee = -2
        for i in range(len(self.peers)):
            if not self.peers[i].crashed:           # count only non crashed processes
                if self.peers[i].elected == -1:  
                    return [False, -1]
                else:
                    # check that all nodes elected the same coordinator
                    if electee == -2:
                        electee = self.peers[i].elected
                    elif electee != -1:
                        if electee != self.peers[i].elected :
                            electee = -1

        return [True, electee]

    # resets node to default status
    def reset(self, env):
        self.blocked = False
        self.crashed = False
        self.elected = -1
        self.el_in_progress = False
        self.missing_ack = []
        self.env = env
        self.queue = Store(env)
        self.wait_msg = env.event()
        # ID of greatest node that gave OK
        self.max_active_id = -1
        # for sim stats
        self.sim_id+=1
        
    
    # sets wether election happens with reliable or unreliable links with a network packet loss rate and if debug messages are activated
    def set_behaviour(self, loss_rate, debug_mode = False):
        self.loss_rate = loss_rate
        self.debug_mode = debug_mode
