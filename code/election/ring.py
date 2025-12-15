from numpy import random
import simpy

from msg.ring_msg import ElectionRingMsg
from node.ring_node import RingNode
from election.simulation import Simulation
from utils import max_delay

# this class represents a ring algorithm simulation
#   attributes:
#       - env -> simpy env
#       - n_nodes -> number of nodes in the net
#       - delay_mean -> exponential mean for setting propagation delays
#       - sim_stats -> SimStats class representing the simulation
#       - n_initiators -> number of initiators 
#       - unreliable -> boolean value, if true the algorithm performs the 
#                       algorithm with unreliable links assumption 
#       - loss -> loss rate of packets (unreliable)
#       - timeout -> max timeout to wait (unreliable)
#       - debug_mode -> if true the nodes and this class will print debug messages
#       - nodes -> nodes of the network
class RingSimulation(Simulation):
    
    def __init__(self, env, n_nodes, delay_mean, sim_stats, n_initiators = 1, unreliable = False, loss=0.0, timeout=0.0, debug_mode=False, rng=None):
        super().__init__(env, n_nodes, delay_mean)
        self.sim_stats = sim_stats
        self.n_initiators = n_initiators
        self.unreliable = unreliable
        self.loss=loss
        self.timeout = max_delay(timeout, delay_mean)
        self.stats_id = 0
        self.debug_mode = debug_mode
        self.rng = rng          # debug

        for i in range(n_nodes):        # create nodes with IDs i = 0, 1, 2, ...
            self.nodes.append(RingNode(env, i, delay_mean, self.unreliable, debug_mode, loss, self.timeout, self.rng, self.stats_id, sim_stats))

        for i in range(n_nodes):        # pass the peers to the nodes
            self.nodes[i].obtain_peers(self.nodes)

        self.add_triggers()

    def __str__(self):
        return (
            f"- Number of nodes: {self.n_nodes}\n"
            f"- Number of initiators: {self.n_initiators}\n"
            f"- Unreliability: {self.unreliable}\n"
            f"- Timeout: {self.timeout}\n"
            f"- Delay mean: {self.delay_mean}\n"
            f"- Loss: {self.loss}"
        )

    # method to start an election; starting conditions: coordinator crashed and n initiators
    def start_election(self):

        if self.debug_mode:
            print("------------------------------------------------\n")
            print(f"Time {self.env.now:.2f}: Start Ring election algorithm\n")

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

        if self.debug_mode:
            print("\nRing election algorithm terminated")
            print("\n------------------------------------------------\n")

        raise simpy.core.StopSimulation("Election finished")        # stop all processes

    def clean(self, env):
        super().clean(env)
        self.finish_event = self.env.event()
        self.sim_stats.clear_delays(self.stats_id)
        self.stats_id += 1
        
        for i in range(self.n_nodes):
            self.nodes.append(RingNode(self.env, i, self.delay_mean, self.unreliable, self.debug_mode, self.loss, self.timeout, self.rng, self.stats_id, self.sim_stats))
            
        # pass the peers to the nodes
        for i in range(self.n_nodes):
            self.nodes[i].obtain_peers(self.nodes)

        self.add_triggers()
