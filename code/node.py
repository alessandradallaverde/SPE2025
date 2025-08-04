from msg import BullyMsg, RingMsg
from simpy import Store

# useful functions
# compares two integers
def cmp(a, b):
    return (a > b) - (a < b)

class Node:

    def __init__(self, env, id):
        self.id = id                                       
        #self.free = True
        self.queue = Store(env)
        self.crashed = False
        self.env = env

    def obtain_peers(self, peers):
        self.peers = peers

    def crash(self):
        self.crashed = True

# this class represents a node in the ring algorithm execution
class RingNode(Node):

    def __init__(self, env, id):
       super().__init__(env, id)
       self.participant = False
       self.elected = -1

    def send(self, type, vote_id):
        
        # create the election message 
        election_msg = RingMsg(type, vote_id)

        # find the next active neighbor
        next = self.find_neighbor()

        # DEBUG
        print(f"Node {self.id} sends {type} with ID {vote_id} to node {next}")

        # message delay -> must be modified with exponential delays
        # OBS: the time is not milliseconds, it is an arbitrary unit, we
        #      decide what it is
        yield self.env.timeout(20)

        # send the message 
        yield self.peers[next].queue.put(election_msg) 
        self.env.process(self.peers[next].receive())


    def receive(self):
        # OBS: the get waits until there is something in the store
        msg = yield self.queue.get()
        if msg.type == "ELECTION":
            # DEBUG
            print(f"Node {self.id} receives ELECTION with ID {msg.id}")

            match cmp(msg.id, self.id) :
                case -1: # msg id less than self id
                    if self.participant == False:
                        self.participant = True

                        # the node sends an election message with its id
                        # to its next (active) neighbor
                        self.env.process(self.send("ELECTION",self.id))
                case 0: # msg id equal to self id
                    # DEBUG
                    print(f"Node {self.id} announces itself as coordinator")

                    self.participant = False
                    self.elected = self.id

                    # the node sends a coordinator message to its next (active) 
                    # neighbor
                    self.env.process(self.send("COORDINATOR",self.id))
                case 1: # msg id greater than self id
                    self.participant = True

                    # the node sends an election message with the message id to 
                    # its next active neighbor
                    self.env.process(self.send("ELECTION",msg.id))
        elif msg.type == "COORDINATOR":
            if self.id != msg.id:
                # DEBUG
                print(f"Node {self.id} elects {msg.id} as coordinator")

                self.participant = False
                self.elected = msg.id

                # the node sends a coordinator message with the message id to 
                # its next active neighbor
                self.env.process(self.send("COORDINATOR",msg.id))
            else:
                # DEBUG
                print(f"Everyone agree on the coordinator")

    # find the next active neighbor
    def find_neighbor(self):
        for i in range(1,len(self.peers)):
            next = self.peers[(i+self.id)%len(self.peers)];
            if next.crashed == False:
                return next.id
            


# this class represents a node in the bully algorithm execution
class BullyNode(Node):

    def __init__(self, env, id):
       super().__init__(env, id)
       self.elected = -1
       self.is_waiting = False
       self.blocked = False

    def send(self, type, dest_id):
        if not self.peers[dest_id].crashed:
            # create the election message 
            election_msg = BullyMsg(type, self.id)

            # DEBUG
            print(f"Node {self.id} sends {type} to node {dest_id}")
            
            yield self.env.timeout(20)
            # send the message 
            yield self.peers[dest_id].queue.put(election_msg) 
            self.env.process(self.peers[dest_id].receive())


    def receive(self):
        msg = yield self.queue.get()
        if msg.type == "ELECTION":
            if msg.sender_id == -1:
                # start election
                print(f"Node {self.id} detected coordinator crash")
            else:    
                # DEBUG
                print(f"Node {self.id} receives ELECTION message from node {msg.sender_id}")

            if self.id > msg.sender_id:
                if msg.sender_id != -1:
                    # if id is greater than sender: stop election
                    self.env.process(self.send("OK", msg.sender_id))
                if not self.is_waiting:
                    # only start election ONCE
                    self.is_waiting = True
                    # send ELECTION messages to all nodes with greater id
                    for i in range(self.id + 1, len(self.peers)):
                        self.env.process(self.send("ELECTION", i))
                    # TO BE CHANGED: works in synchronous systems where you have an upper bound of network delays
                    yield self.env.timeout(40 * len(self.peers) + 1)
                    self.is_waiting = False
                    #   wait for a certain time to be passed ... if it wasn't stopped it is elected
                    if not self.blocked:
                        for i in range(len(self.peers)):
                            self.env.process(self.send("COORDINATOR", self.peers[i].id))

        elif msg.type == "OK":
            # DEBUG
            print(f"Node {self.id} receives OK message from node {msg.sender_id}")
            # stop election
            self.blocked = True

        elif msg.type == "COORDINATOR":
            # DEBUG
            print(f"Node {self.id} elects {msg.sender_id} as coordinator")
            self.elected = msg.sender_id
            # if election terminated trigger finish event
            if self.finished():
                self.finish.succeed()

    # returns True if all nodes decided on coordinator
    def finished(self):
        for i in range(len(self.peers)):
            if self.peers[i].elected == -1 and not self.peers[i].crashed:     # count only non crashed processes
                return False
        return True      

    def reset(self):
        self.blocked = False
        self.crashed = False
        self.elected = -1
        self.is_waiting = False      
