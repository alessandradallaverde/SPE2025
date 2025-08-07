from numpy import random

from msg.ring_msg import RingMsg
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
        election_msg = RingMsg("ELECTION", -1)

        # starts election
        yield initiator.queue.put(election_msg) 
        self.env.process(initiator.receive())

        # starts crashes
        # self.env.process(self.insert_crash())

        # starts initiators 
        # self.env.process(self.insert_initiator())

    # method to insert a random initiator in the network 
    # TODO: modify because an initiator can't exist if has received an election 
    #       message
    def insert_initiator(self):
    
        while(True):

            yield self.env.timeout(self.delay_mean*3)

            # choose an initiator
            new_initiator = self.nodes[random.randint(len(self.nodes))]
            # if the initiator is crashed or is already an initiator choose another one
            while new_initiator.crashed or new_initiator.initiator:
                new_initiator = self.nodes[random.randint(len(self.nodes))]

            new_initiator.initiate()

            # create the election message 
            election_msg = RingMsg("ELECTION", -1)

            # starts election
            yield new_initiator.queue.put(election_msg) 
            self.env.process(new_initiator.receive())
    
    # method to crash a random node
    # TODO: testing because it has some problems
    def insert_crash(self):
        # a node crashes 
        while(self.crashes<len(self.nodes)-1):
            
            yield self.env.timeout(self.delay_mean*10)

            crash_node = self.nodes[random.randint(len(self.nodes))]
            # if the node is already crashed find another one
            while crash_node.crashed:
                crash_node = self.nodes[random.randint(len(self.nodes))]

            crash_node.crash()
            self.crashes +=1