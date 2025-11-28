# this class represents a simulation of an election
#
# attributes
#   - env -> simpy environment
#   - nodes -> network nodes
#   - finish_event -> simpy event triggered when a coordinator is elected
class Simulation:

    def __init__(self, env, n_nodes, delay_mean):
        self.env = env
        self.nodes = []
        self.finish_event = self.env.event()
        self.t_time = 0
        self.n_nodes = n_nodes
        self.delay_mean = delay_mean

    # method to add triggers to the nodes
    def add_triggers(self):
        for i in range(len(self.nodes)):
            # add reference to 'finish_event' so that nodes can trigger it
            self.nodes[i].finish = self.finish_event

    # method to get the turnaround time of the simulation
    def get_t_time(self):
        return self.t_time

    # method to clean the class and to set a new environment with a specified 
    # number of nodes
    def clean(self, env):
        self.env = env
        self.nodes.clear()
        self.t_time = 0