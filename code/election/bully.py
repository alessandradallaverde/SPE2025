from numpy import random

from msg.bully_msg import BullyMsg
from node.bully_node import BullyNode
from election.simulation import Simulation

# this class represents a bully algorithm simulation
class BullySimulation(Simulation):
    
    def __init__(self, env, n_nodes):

        super().__init__(env, n_nodes)

        for i in range(n_nodes):
            self.nodes.append(BullyNode(env, i))

        # pass the peers to the nodes
        for i in range(n_nodes):
            self.nodes[i].obtain_peers(self.nodes)

    # method to start an election
    def start_election(self, n_initiators = 1, loss_rate = 0):
        # reject operation if initiators are too many
        if n_initiators > (len(self.nodes) - 1):
            print("\031[1;94m------------------------------------------------\n")
            print("OPERATION REJECTED: number of initiators greater than non-coordinator nodes!\033[0m\n")
            return

        # restore all nodes default status
        for i in range(len(self.nodes)):
            self.nodes[i].reset()
            self.nodes[i].set_behaviour(loss_rate)
            
        self.finish_event = self.env.event()
        self.add_triggers()

        print("\033[1;94m------------------------------------------------\n")
        print("Start Bully election algorithm\033[0m\n")
        
        # coordinator (crashed)
        self.nodes[len(self.nodes)-1].crash()
        
        # there can be multiple nodes that detect coordinator crash
        initiators = []
        for i in range(n_initiators):
            init = self.nodes[random.randint(len(self.nodes))]
            # if generated initiator is the crashed coordinator, generate a new one
            while init.crashed or init in initiators:
                init = self.nodes[random.randint(len(self.nodes))]

            initiators.append(init)

        # all initiators start election
        election_msg = BullyMsg("ELECTION", -1)
        for i in range(n_initiators):
            yield initiators[i].queue.put(election_msg) 
            if loss_rate == 0:
                # reliable links
                self.env.process(initiators[i].reliable_receive())
            else:
                self.env.process(initiators[i].unreliable_receive())

        # wait for finish_event to be triggered (means that election ended)
        yield self.finish_event

        self.t_time = self.env.now
        # DEBUG
        print("\n\033[1;94mBully election algorithm terminated")
        print("\n------------------------------------------------\033[0m\n")

        def clean(self, env):
            super().clean(env)

            for i in range(self.n_nodes):
                self.nodes.append(BullyNode(env, i))

            # pass the peers to the nodes
            for i in range(self.n_nodes):
                self.nodes[i].obtain_peers(self.nodes)