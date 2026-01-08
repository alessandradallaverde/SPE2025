# this class represents a simulation of an election
#   attributes:
#       env - simpy environment
#       n_nodes - network nodes
#       delay_mean - exponential mean for delays
class Simulation:

    def __init__(self, env, n_nodes, delay_mean):
        self.env = env
        self.nodes = []
        self.finish_event = self.env.event()
        self.n_nodes = n_nodes
        self.delay_mean = delay_mean

    # method to add event trigger to the nodes
    def add_triggers(self):
        for i in range(len(self.nodes)):
            # add reference to 'finish_event' so that nodes can trigger it
            self.nodes[i].finish = self.finish_event

    # method to clean the class and to set a new environment with a specified 
    # number of nodes
    #    params:
    #        env - simpy environment
    def clean(self, env):
        self.env = env
        self.nodes.clear()
        self.t_time = 0