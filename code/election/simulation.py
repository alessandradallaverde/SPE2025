# this class represents a simulation of an election
#
# attributes
#   - env -> simpy environment
#   - nodes -> network nodes
#   - finish_event -> simpy event triggered when a coordinator is elected
class Simulation:

    def __init__(self, env):
        self.env = env
        self.nodes = []
        self.finish_event = self.env.event()

    # method to add triggers to the nodes
    def add_triggers(self):
        for i in range(len(self.nodes)):
            # add reference to 'finish_event' so that nodes can trigger it
            self.nodes[i].finish = self.finish_event