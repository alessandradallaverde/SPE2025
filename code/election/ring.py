from numpy import random

from msg.ring_msg import ElectionRingMsg
from node.ring_node import RingNode

# this class represents a ring algorithm simulation
#   attributes:
#       - finish -> boolean value, if true the algorithm has finished
#       - env -> simpy environment
#       - delay_mean -> exponential mean for setting propagation delays
#       - initiators -> boolean value, if true the algorithm insert multiple
#                       initiators 
#       - crashes -> number of crashed nodes in the system
#       - unreliable -> boolean value, if true the algorithm performs the 
#                       algorithm with unreliable links assumption 
#       - nodes -> nodes of the network
class RingSimulation:
    
    def __init__(self, env, N_NODES, finish, delay_mean, initiators = False, unreliable = False):
        self.finish = finish
        self.env = env
        self.delay_mean = delay_mean

        self.initiators = initiators
        self.crashes = 0
        self.unreliable = unreliable

        self.nodes = []
        for i in range(N_NODES):        # create nodes with IDs i = 0, 1, 2, ...
            self.nodes.append(RingNode(env, i, self.delay_mean, self.unreliable))

        for i in range(N_NODES):        # pass the peers to the nodes
            self.nodes[i].obtain_peers(self.nodes)


    # method to start an election
    # OBS - starting conditions: coordinator crashed and one single initiator
    def start_election(self):

        print("------------------------------------------------\n")
        print(f"Time {self.env.now:.2f}: Start Ring election algorithm\n")

        self.nodes[len(self.nodes)-1].crash()       # the coordinator crashes (it is the one with the bigger ID)
        self.crashes +=1

        initiator = self.nodes[random.randint(len(self.nodes)-1)]       # choose a random initiator
        initiator.initiate()
            
        election_msg = ElectionRingMsg(initiator.id,-1,[])      # starts election
        yield initiator.queue.put(election_msg) 

        if self.initiators:
            self.env.process(self.insert_initiator())       # starts initiators 


    # method to insert random initiators in the network 
    def insert_initiator(self):

        i = 0
    
        while True:     # continues iterating until there are no more possible initiators

            # TODO: decide how to set this timeout
            yield self.env.timeout(self.delay_mean*2) 

            while(i<len(self.nodes)):

                new_initiator = self.nodes[i]

                # if the node isn't already an initiator, crashes or is participating in the election
                if not(new_initiator.crashed or new_initiator.initiator or new_initiator.participant):
                    new_initiator.initiate()
                    election_msg = ElectionRingMsg(new_initiator.id,-1,[])
                    yield new_initiator.queue.put(election_msg) 
                    break

                i+=1

            if i == len(self.nodes):    # there are no more nodes able to initiate the election algorithm
                break

            i=0
