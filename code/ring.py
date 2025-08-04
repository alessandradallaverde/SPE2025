from numpy import random
from msg import RingMsg

# this class represents a ring algorithm simulation
class RingSimulation:
    
    def __init__(self, env, nodes, finish):
        self.nodes = nodes
        self.finish = finish
        self.env = env

    # method to start an election
    def start_election(self):

        print("Start Ring election algorithm")

        yield self.env.timeout(1)
        # the coordinator crashes (it is the one with the bigger ID)
        # (remember that we can have more than one node crashed)
        self.nodes[len(self.nodes)-1].crash()

        # choose an initiator -> must be modified because we can have more than 
        #                        one node that detects coordinator crash
        initiator = self.nodes[random.randint(len(self.nodes))]
        # if the initiator is crashed choose another one
        while initiator.crashed == True:
            initiator = self.nodes[random.randint(len(self.nodes))]
            
        # create the election message 
        election_msg = RingMsg("ELECTION", -1)

        # starts election
        yield initiator.queue.put(election_msg) 
        self.env.process(initiator.receive())