from msg import Msg, ringMsg
from simpy import Process, Store

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


    '''
    
    def process_msg(self, msg):
        self.queue.append(msg)

        if self.free:
            if self.queue.__len__() != 0:
                self.free = False
                msg = self.queue.pop(0)

                self.log_msg(msg)       
                #   type to test message sending functionality         
                if msg.type == "READY":
                    self.send( msg.sender_id, "ACK" )

                self.free = True
    

    def send(self, dest_id, msg_type):
        #   network delays?
        self.peers[dest_id].receive(Msg(msg_type, self.id))
    
    def multicast(self, msg_type):
        #   for better network delays reorder nodes before multicast
        for i in range(self.peers.__len__()):
            if self.id != i:
                self.send(i, msg_type)

    def receive(self, msg):
        if not self.crashed:
            self.process_msg(msg)
    
    
    def start_bully_election(self):
        print("Start Bully election algorithm")
    

    def log_msg(self, msg):        
        print( self.to_string() + ": " + self.peers[msg.sender_id].to_string() + " sent \"" + msg.type + "\"" )
    
    def to_string(self):
        return "Node " + str(self.id)
    '''

# this class represents a node in the ring algorithm execution
class ringNode(Node):

    def __init__(self, env, id):
       super().__init__(env, id)
       self.participant = False
       self.elected = -1

    def send(self, type, vote_id):
        
        # create the election message 
        election_msg = ringMsg(type, vote_id)

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