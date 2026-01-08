from numpy import random

from msg.bully_msg import BullyMsg
from node.bully_node import BullyNode
from election.simulation import Simulation

# this class represents a bully algorithm simulation
#   attributes:
#       nodes - list of nodes in the network
#       finish_event - event to be triggered to stop the algorithm execution
#       t_time - simulation turnaround time
#       sim_stats - reference to the statistics class to record stats during simulations
#       env - simulation environment
class BullySimulation(Simulation):
    
    # method to initialize BullySimulation
    #   params:
    #       env - simulation environment
    #       n_nodes - number of nodes 
    #       delay_mean - mean of exponential delays
    #       delay_q - quantile to determine max delay considered by the system
    #       sim_stats - reference to the statistics class to record stats during simulations
    def __init__(self, env, n_nodes, delay_mean, delay_q, sim_stats):

        super().__init__(env, n_nodes, delay_mean)
        self.sim_stats = sim_stats

        for i in range(n_nodes):
            self.nodes.append(BullyNode(env, i, sim_stats, -1, delay_mean, delay_q))

        for i in range(n_nodes):            # pass the peers to the nodes
            self.nodes[i].obtain_peers(self.nodes)

    # method to start an election
    #   params:
    #       n_initiators - number of initiators
    #       loss_rate - packets loss rate
    #       debug_mode - if true the nodes and this class will print debug messages
    def start_election(self, n_initiators = 1, loss_rate = 0, debug_mode = False):
        if n_initiators > (len(self.nodes) - 1):        # reject operation if initiators are too many
            print("\031[1;94m------------------------------------------------\n")
            print("OPERATION REJECTED: number of initiators greater than non-coordinator nodes!\033[0m\n")
            return
        
        self.sim_stats.clear_delays(len(self.sim_stats.msg_counter)-1)      # restore all nodes default status
        for i in range(len(self.nodes)):
            self.nodes[i].reset(self.env)
            self.nodes[i].set_behaviour(loss_rate, debug_mode)
            
        self.finish_event = self.env.event()
        self.add_triggers()

        if debug_mode:
            print("\033[1;94m------------------------------------------------\n")
            print("Start Bully election algorithm\033[0m\n")
        
        self.nodes[len(self.nodes)-1].crash()           # coordinator (crashed)
        
        initiators = []          # select random initiators
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
            if loss_rate == 0:          # reliable links
                self.env.process(initiators[i].reliable_receive())
            else:
                self.env.process(initiators[i].unreliable_receive())

        # wait for finish_event to be triggered (means that election ended)
        result = yield self.finish_event
        if result < 0:
            self.sim_stats.add_wrong_sim()
        self.t_time = self.env.now
        self.sim_stats.add_runtime(self.env.now)            # stat counter
        
        if debug_mode:
            print("\n\033[1;94mBully election algorithm terminated")
            print("\n------------------------------------------------\033[0m\n")