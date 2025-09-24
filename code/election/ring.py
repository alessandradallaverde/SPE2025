from numpy import random
import simpy

from msg.ring_msg import ElectionRingMsg
from node.ring_node import RingNode
from election.simulation import Simulation

# this class represents a ring algorithm simulation
#   attributes:
#       - delay_mean -> exponential mean for setting propagation delays
#       - n_initiators -> number of initiators 
#       - unreliable -> boolean value, if true the algorithm performs the 
#                       algorithm with unreliable links assumption 
#       - nodes -> nodes of the network
class RingSimulation(Simulation):
    
    def __init__(self, env, n_nodes, delay_mean, sim_stats, n_initiators = 1, unreliable = False):
        super().__init__(env, n_nodes, delay_mean)
        self.n_initiators = n_initiators
        self.unreliable = unreliable
        self.sim_stats = sim_stats

        for i in range(n_nodes):        # create nodes with IDs i = 0, 1, 2, ...
            self.nodes.append(RingNode(env, i, delay_mean, self.unreliable))

        for i in range(n_nodes):        # pass the peers to the nodes
            self.nodes[i].obtain_peers(self.nodes)

        self.add_triggers()

    # method to start an election; starting conditions: coordinator crashed and n initiators
    def start_election(self):

        # DEBUG
        # print("------------------------------------------------\n")
        # print(f"Time {self.env.now:.2f}: Start Ring election algorithm\n")

        self.nodes[len(self.nodes)-1].crash()       # the coordinator crashes (it is the one with the bigger ID)

        initiators = []
        i=0

        while i<self.n_initiators:      # select n random initiators
            id=random.randint(len(self.nodes)-1)
            if id not in initiators:
                initiators.append(id)
                i+=1
        
        for id in initiators:       # start elections
            initiator = self.nodes[id]
            initiator.initiate()
            election_msg = ElectionRingMsg(initiator.id,-1,[])      # starts election
            yield initiator.queue.put(election_msg)
         
        yield self.finish_event     # wait for finish_event to be triggered

        # store in stats
        self.sim_stats.add_runtime(self.env.now)

        # DEBUG
        # print("\nRing election algorithm terminated")
        # print("\n------------------------------------------------\n")

        raise simpy.core.StopSimulation("Election finished")        # stop all processes

    def clean(self, env):
        super().clean(env)
        self.finish_event = self.env.event()

        for i in range(self.n_nodes):
            self.nodes.append(RingNode(env, i, self.delay_mean, self.unreliable))
            
        # pass the peers to the nodes
        for i in range(self.n_nodes):
            self.nodes[i].obtain_peers(self.nodes)

        self.add_triggers()
