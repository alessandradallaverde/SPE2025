# this class represents the statistics for multiple simulations of an election
# algorithm with the same factors
#
#   attributes:
#       initiators - number of initiators
#       delay - delay (exponential mean) chosen for the simulation
#       n_nodes - number of nodes in the net
#       timeout - timeout for messages under unreliable links condition
#       loss_rate - prob. that a message isn't received under unreliable links condition
#       t_times - list containing turnaround time for each identical simulation
class SimStats:
    def __init__(self, initiators, delay, n_nodes, timeout=-1, loss_rate=-1):
        self.initiators = initiators
        self.delay = delay
        self.n_nodes = n_nodes
        self.timeout = timeout
        self.loss_rate = loss_rate

        self.t_times = []

    def add_turnaround_time(self, t_time):
        self.t_times.append(t_time)

    def get_t_times(self):
        return self.t_times

    # TODO
    def compute_ci(self):
        pass

    # TODO
    def compute_mean(self):
        pass

    # TODO
    def compute_var(self):
        pass

# this class represents the statistics result of different simulation with 
# different factors, it is used to create plots/further analysis and to 
# analyze factors
#   
#   attributes:
#       stats: a list of SimStat objects
class StatsManager:
    def __init__(self):
        self.stats = []

    def insert_stat(self, sim_stat):
        self.stats.append(sim_stat)
