from numpy import random

from msg.ring_msg import ElectionRingMsg
from node.ring_node import RingNode

# this class represents a ring algorithm simulation
class RingSimulation:
    
    def __init__(self, env, N_NODES, finish, delay_mean):
        self.finish = finish
        self.env = env
        self.delay_mean = delay_mean
        self.crashes = 0

        # create nodes with IDs i = 0, 1, 2, ...
        self.nodes = []
        for i in range(N_NODES):
            self.nodes.append(RingNode(env, i, self.delay_mean))

        # pass the peers to the nodes
        for i in range(N_NODES):
            self.nodes[i].obtain_peers(self.nodes)


    # method to start an election
    # OBS: for now we start with one initiator and the coordinator crashed
    def start_election(self):

        print("------------------------------------------------\n")
        print(f"Time {self.env.now:.2f}: Start Ring election algorithm\n")

        # the coordinator crashes (it is the one with the bigger ID)
        self.nodes[len(self.nodes)-1].crash()
        self.crashes +=1

        # choose an initiator
        initiator = self.nodes[random.randint(len(self.nodes)-1)]
        initiator.initiate()
            
        # create the election message 
        election_msg = ElectionRingMsg([])

        # starts election
        yield initiator.queue.put(election_msg) 
        #self.env.process(initiator.receive())

        # starts initiators 
        self.env.process(self.insert_initiator())

        # starts crashes
        # self.env.process(self.insert_crash())

    # method to insert a random initiator in the network 
    def insert_initiator(self):

        i = 0
    
        # while there may be nodes that can start a new election
        while True:

            # wait
            # TODO: decide how to set this timeout
            yield self.env.timeout(self.delay_mean*2)

            # find the node to initiate
            while(i<len(self.nodes)):

                new_initiator = self.nodes[i]

                if not(new_initiator.crashed or new_initiator.initiator or new_initiator.participant):
                    new_initiator.initiate()

                    # create the election message 
                    election_msg = ElectionRingMsg([])

                    # starts election
                    yield new_initiator.queue.put(election_msg) 

                    break;

                i+=1

            # there are no more nodes able to initiate the election algorithm
            if i == len(self.nodes):
                break

            i=0


    # method to crash a random node
    def insert_crash(self):
        pass