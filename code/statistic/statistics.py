import math
from numpy import random 
import matplotlib.pyplot as plt

# this class represents the statistics for multiple simulations of an election
# algorithm with the same factors
#
#   attributes:
#       initiators - number of initiators
#       delay - delay (exponential mean) chosen for the simulation
#       n_nodes - number of nodes in the net
#       timeout - timeout for messages under unreliable links condition
#       loss_rate - prob. that a message isn't received under unreliable links condition
#       rtt_times - list containing turnaround time for each identical simulation
#       runtimes - list containing runtime for each simulation
class SimStats:
    def __init__(self, initiators, delay, n_nodes, timeout=-1, loss_rate=-1):
        self.initiators = initiators
        self.delay = delay
        self.n_nodes = n_nodes
        self.timeout = timeout
        self.loss_rate = loss_rate

        self.runtimes = []

    def add_runtime(self, t_time):
        self.runtimes.append(t_time)

    
    def get_runtimes(self):
        return self.runtimes

    # computes mean of one of the statistics list
    def compute_mean(self, stats):
        mean = 0
        for el in stats:
            mean += el

        return (mean/len(stats))

    # works similarly to the compute_mean() function, but measuring variance
    def compute_var(self, mean, stats):
        var = 0
        for el in stats:
            var += ((el - mean)**2)

        return (var/len(stats))

    # method to compute asymptotic CI 95% confidence
    def compute_ci(self):
        mean = self.compute_mean(self.runtimes)
        var = self.compute_var(mean, self.runtimes)
        err = 1.96 * math.sqrt(var / self.n_nodes)

        return err

    def plot_runtimes_hist(self, bins):
        plt.figure()
        plt.hist(self.runtimes, bins=bins, label = "Simulations with reliable links" )
        plt.xlim()
        plt.xlabel("Runtime in ms")
        plt.legend()

    def plot_runtimes_box_plot(self):
        plt.figure()
        plt.boxplot(self.runtimes)
        plt.title("Box Plot")
        plt.ylabel("Turnaround Times")

    # method to compute bootstrap ci
    # parameters:
    # ci_level          ->  confidence level
    # stat_function     ->  reference to the function that can compute the needed statistic (mean, variance, ect.)
    # stats             ->  list of data
    def bootstrap_stats(self, ci_level, stat_function, stats):
        
        r0 = math.floor(((1 - ci_level) * len(stats)) / 2)
        R = math.ceil(2 * r0 / (1 - ci_level)) - 1
        boot_stat = []
        for i in range(R):
            # draw n & compute stats
            draw = []
            for j in range(len(stats)):
                index = random.randint(0, len(stats))
                draw.append(stats[index])
            
            boot_stat.append(stat_function(draw))
        # sort
        boot_stat.sort()
        return (boot_stat[r0], boot_stat[R + 1 -r0])


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

