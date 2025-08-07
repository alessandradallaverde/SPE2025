from numpy import random
from msg.bully_msg import BullyMsg
from node.bully_node import BullyNode

# this class represents a bully algorithm simulation
class BullySimulation:
    
    def __init__(self, env, n_nodes):
        self.env = env

        self.nodes = []
        for i in range(n_nodes):
            self.nodes.append(BullyNode(env, i))

        # pass the peers to the nodes
        for i in range(n_nodes):
            self.nodes[i].obtain_peers(self.nodes)

    # method to start an election
    def start_election(self):
        # restore all nodes default status
        for i in range(len(self.nodes)):
            self.nodes[i].reset()
            
        self.finish_event = self.env.event()
        self.add_triggers()

        print("------------------------------------------------\n")
        print("Starting Bully election algorithm\n")
        
        # coordinator (crashed)
        self.nodes[len(self.nodes)-1].crash()
        
        initiator = self.nodes[random.randint(len(self.nodes))]
        # if the initiator is crashed choose another one
        while initiator.crashed :
            initiator = self.nodes[random.randint(len(self.nodes))]
            
        # create the election message 
        election_msg = BullyMsg("ELECTION", -1)
        # starts election
        yield initiator.queue.put(election_msg) 
        self.env.process(initiator.receive())

        # wait for finish_event to be triggered (means that election ended)
        yield self.finish_event
        print("\nBully election algorithm terminated")
        print("\n------------------------------------------------\n")

    def add_triggers(self):
        for i in range(len(self.nodes)):
            # add reference to 'finish_event' so that nodes can trigger it
            self.nodes[i].finish = self.finish_event