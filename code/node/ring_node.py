from node.node import Node
from msg.ring_msg import RingMsg

import utils

# this class represents a node in the ring algorithm execution
class RingNode(Node):

    def __init__(self, env, id, delay_mean):
       super().__init__(env, id)
       self.participant = False
       self.elected = -1
       self.initiator = False
       self.delay_mean = delay_mean

    def initiate(self):
        self.initiator = True

        # DEBUG
        print(f"Time {self.env.now:.2f}: Node {self.id} initiates an election")

    def send(self, type, vote_id):

        # message delay -> must be modified with exponential delays
        yield self.env.timeout(utils.delay(self.delay_mean))

        # create the election message 
        election_msg = RingMsg("ELECTION",-1) if self.peers[vote_id].crashed else RingMsg(type, vote_id)
        # find the next active neighbor
        next = self.find_neighbor()
        yield self.peers[next].queue.put(election_msg) 
        self.env.process(self.peers[next].receive())

        # DEBUG
        print(f"Time {self.env.now:.2f}: Node {self.id} sends {type} with ID {vote_id} to node {next}")


    def receive(self):
        # OBS: the get waits until there is something in the store
        msg = yield self.queue.get()
        if msg.type == "ELECTION":
            # DEBUG
            print(f"Time {self.env.now:.2f}: Node {self.id} receives ELECTION with ID {msg.id}")

            match utils.cmp(msg.id, self.id) :
                case -1: # msg id less than self id
                    if self.participant == False:
                        self.participant = True

                        # the node sends an election message with its id
                        # to its next (active) neighbor
                        yield self.env.timeout(utils.delay(self.delay_mean))
                        self.env.process(self.send("ELECTION",self.id))
                case 0: # msg id equal to self id
                    # DEBUG
                    print(f"Time {self.env.now:.2f}: Node {self.id} announces itself as coordinator")

                    self.participant = False
                    self.elected = self.id

                    # the node sends a coordinator message to its next (active) 
                    # neighbor
                    yield self.env.timeout(utils.delay(self.delay_mean))
                    self.env.process(self.send("COORDINATOR",self.id))
                case 1: # msg id greater than self id
                    self.participant = True

                    # the node sends an election message with the message id to 
                    # its next active neighbor
                    yield self.env.timeout(utils.delay(self.delay_mean))
                    self.env.process(self.send("ELECTION",msg.id))
        elif msg.type == "COORDINATOR":
            if self.id != msg.id:
                # DEBUG
                print(f"Time {self.env.now:.2f}: Node {self.id} elects {msg.id} as coordinator")

                self.participant = False
                self.elected = msg.id

                # the node sends a coordinator message with the message id to 
                # its next active neighbor
                yield self.env.timeout(utils.delay(self.delay_mean))
                self.env.process(self.send("COORDINATOR",msg.id))
            else:
                # DEBUG
                print(f"Time {self.env.now:.2f}: Everyone agree on the coordinator")
                print("\nRing election algorithm terminated\n")

    # find the next active neighbor
    def find_neighbor(self):
        for i in range(1,len(self.peers)):
            next = self.peers[(i+self.id)%len(self.peers)];
            if next.crashed == False:
                return next.id