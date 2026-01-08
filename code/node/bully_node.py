from numpy import random
from node.node import Node
from msg.bully_msg import BullyMsg
from utils import delay, max_delay
from simpy import Store, core, AnyOf

# this class represents a node in the bully algorithm execution
#   attributes:
#       elected - id of the new coordinator
#       el_in_progress - true if the node is already participating in the election
#       blocked - true if the node received at least an OK message
#       missing_ack - list of nodes ids for which the node is waiting an ack
#       max_wait - max timeout to wait (unreliable)
#       sim_stats - reference to the SimStats of the simulation
#       sim_id - unique id of the execution for the SimStats of the simulation
#       crashed - if true, the node crashed
#       queue - messages queue 
#       wait_msg - event to be triggered if all the acks were received
#       max_active_id - id of greatest node that gave OK
#       loss_rate - packets loss rate
#       debug_mode - if true the nodes and this class will print debug messages
#       finish - reference to the event to trigger to stop the election
#       peers - network nodes
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

    # method to send message with reliable links
    #   params:
    #       type - message type
    #       dest_id - destination node id
    def reliable_send(self, type, dest_id):
        
        if not self.peers[dest_id].crashed:
            election_msg = BullyMsg(type, self.id)      # create the election message

            if self.debug_mode:
                print(f"Time {self.env.now:.2f}: Node {self.id} sends {type} to node {dest_id}")

            msg_delay = delay(self.delay_mean)
            self.sim_stats.add_msg(self.sim_id, msg_delay)      # increase message counter
            yield self.env.timeout(msg_delay)
            yield self.peers[dest_id].queue.put(election_msg)       # send the message
            self.env.process(self.peers[dest_id].reliable_receive())

    # method to receive messages with reliable links
    def reliable_receive(self):
        
        msg = yield self.queue.get()
        if msg.type == "ELECTION":
            
            if self.debug_mode:
                if msg.sender_id == -1:     # begin of the election
                    print(f"\033[94mTime {self.env.now:.2f}: Node {self.id} detected coordinator crash\033[0m")
                else:
                    print(f"Time {self.env.now:.2f}: Node {self.id} receives ELECTION message from node {msg.sender_id}")

            if self.id > msg.sender_id:
                if msg.sender_id != -1:     # if id is greater than sender: stop election
                    self.env.process(self.reliable_send("OK", msg.sender_id))
                if not self.el_in_progress:
                    self.el_in_progress = True          # each node can only start election ONCE   
                    for i in range(self.id + 1, len(self.peers)):           # send ELECTION messages to all nodes with greater id
                        self.env.process(self.reliable_send("ELECTION", i))

                    # wait for a certain time to be passed ... if it wasn't stopped it is elected
                    yield self.env.timeout(2 * self.max_wait)
                    if not self.blocked:
                        for i in range(len(self.peers)):
                            self.env.process(
                                self.reliable_send("COORDINATOR", self.peers[i].id))
    
                    self.el_in_progress = False         # election of node ended

        elif msg.type == "OK":
            if self.debug_mode:
                print(f"Time {self.env.now:.2f}: Node {self.id} receives OK message from node {msg.sender_id}")

            self.blocked = True         # stop election

        elif msg.type == "COORDINATOR":
            if self.debug_mode:
                print(f"\033[92mTime {self.env.now:.2f}: Node {self.id} elects {msg.sender_id} as coordinator\033[0m")
            
            self.elected = msg.sender_id
            self.el_in_progress = False         # if active, set election status of node
            is_finished, electee = self.finished()          # if election terminated trigger finish event
            if is_finished:
                self.finish.succeed(electee)        # set value of event
                raise core.StopSimulation("")

    # method to send messages with unreliable links
    #   params:
    #       type - message type
    #       dest_id - destination node id
    def unreliable_send(self, type, dest_id):
        
        if not self.peers[dest_id].crashed:
            election_msg = BullyMsg(type, self.id)          # create the election message
            
            if self.debug_mode:
                print(f"Time {self.env.now:.2f}: Node {self.id} sends {type} to node {dest_id}")

            msg_delay = delay(self.delay_mean)          
            self.sim_stats.add_msg(self.sim_id, msg_delay)      # increase message counter
            if random.uniform(0, 1) > self.loss_rate:       # is packet lost?
                yield self.env.timeout(msg_delay)
                yield self.peers[dest_id].queue.put(election_msg)       # send the message
                self.env.process(self.peers[dest_id].unreliable_receive())
            elif self.debug_mode:
                print(f"\033[31mTime {self.env.now:.2f}: Lost {type} message from node {self.id} to node {dest_id}\033[0m")

    # method to receive messages with unreliable links
    def unreliable_receive(self):
        msg = yield self.queue.get()
        # keep track of highest node id that ever interacted with this node
        self.max_active_id = max(self.max_active_id, msg.sender_id)
        if msg.type == "ELECTION":
            if self.debug_mode:
                if msg.sender_id == -1:         # begin of the election
                    print(f"\033[94mTime {self.env.now:.2f}: Node {self.id} detected coordinator crash\033[0m")
                else:
                    print(f"Time {self.env.now:.2f}: Node {self.id} receives ELECTION message from node {msg.sender_id}")

            if self.id > msg.sender_id:     
                if msg.sender_id != -1:     # if id is greater than sender: stop election
                    self.env.process(self.unreliable_send("OK", msg.sender_id))

                # OPTIMIZATION: don't even start election if you already know of a node with higher ID
                if (not self.el_in_progress) and self.max_active_id <= self.id:
                    # each node can only start election ONCE (retransmissions are not counted)
                    self.el_in_progress = True
                    # send ELECTION messages to all nodes with greater id
                    self.missing_ack = []
                    self.missing_ack.extend(range(self.id + 1, len(self.peers) - 1))
                    yield self.env.process(self.retransmit("ELECTION"))
                    
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
                print(f"Time {self.env.now:.2f}: Node {self.id} receives OK message from node {msg.sender_id}")
            
            self.update_ack_list(msg.sender_id)
            self.blocked = True         # stop election

        elif msg.type == "ACK":
            if self.debug_mode:
                print(f"Time {self.env.now:.2f}: Node {self.id} receives ACK message from node {msg.sender_id}")
            
            self.update_ack_list(msg.sender_id)

        elif msg.type == "COORDINATOR":
            if self.debug_mode:
                print(f"\033[92mTime {self.env.now:.2f}: Node {self.id} elects {msg.sender_id} as coordinator\033[0m")
            
            self.env.process(self.unreliable_send("ACK", msg.sender_id))        # send ACK
            self.elected = msg.sender_id
            
            self.el_in_progress = False         # if active, set election status of node

    # method to udpate ack list counter and trigger appropriate event when all 
    # answers arrived
    #   params:
    #       sender - message sender
    def update_ack_list(self, sender): 
        
        if sender in self.missing_ack:      # remove the node from missing_ack list
            self.missing_ack.remove(sender)

        if len(self.missing_ack) == 0 and not self.wait_msg.triggered:
            self.wait_msg.succeed()     # trigger event
    
    # method to send message that will be retransmitted if not all answers are received
    #   params:
    #       msg_type - message type
    def retransmit(self, msg_type):
        self.wait_msg = self.env.event()
        # OPTIMIZATION
        # If while retransmitting a message you discover a node of higher ID quit
        while len(self.missing_ack) != 0 and not self.blocked:
            for n_id in self.missing_ack:
                self.env.process(self.unreliable_send(msg_type, n_id))
            # set timeout /wait for answers
            yield AnyOf(self.env, [self.wait_msg, self.env.timeout(2 * self.max_wait)])

    # method that return array with two values:
    #   params: 
    #       first - is True if all nodes decided on coordinator
    #       second - is an integer (-1 = different coordinators, otherwise it indicates the node that was elected)
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
    #   params:
    #       env - simpy environment
    def reset(self, env):
        self.blocked = False
        self.crashed = False
        self.elected = -1
        self.el_in_progress = False
        self.missing_ack = []
        self.env = env
        self.queue = Store(env)
        self.wait_msg = env.event()
        self.max_active_id = -1
        self.sim_id+=1
        
    # method to set wether election happens with reliable or unreliable links 
    # with a network packet loss rate and if debug messages are activated
    #   params:
    #       loss_rate - packets loss rate
    #       debug_mode - if true the nodes and this class will print debug messages
    def set_behaviour(self, loss_rate, debug_mode = False):
        self.loss_rate = loss_rate
        self.debug_mode = debug_mode