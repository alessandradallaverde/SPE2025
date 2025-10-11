import math
from numpy import random 
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

# this class represents the statistics for multiple simulations of an election
# algorithm with the same factors
#
#   attributes:
#       initiators - number of initiators
#       delay - delay (exponential mean) chosen for the simulation
#       n_nodes - number of nodes in the net
#       timeout - timeout for messages under unreliable links condition
#       loss_rate - prob. that a message isn't received under unreliable links condition
#       name - name of the simulation
#       id - id of the simulation
#       runtimes - list containing runtime/turnaround time for each simulation
#       mean - mean of the runtimes
#       var - var of the runtimes
#       err - err of the runtimes
class SimStats:
    def __init__(self, initiators, delay, n_nodes, name, unreliable = False, timeout=-1, loss_rate=-1):
        self.initiators = initiators
        self.delay = delay
        self.n_nodes = n_nodes
        self.timeout = timeout
        self.loss_rate = loss_rate
        self.name = name
        self.unreliable=unreliable

        self.runtimes = []
        self.id = -1
        self.mean = 0
        self.var = 0
        self.err = 0

    def __str__(self):
        return (
            f"{self.name} Algorithm:\n"
            f"- Simulations: {len(self.runtimes)}\n"
            f"- Parameters: N = {self.n_nodes}, init = {self.initiators}, mean delay = {self.delay:.2f}\n"
            f"- Turnaround time mean: {self.mean:.2f} \u00B1 {self.err:.2f} ms\n"
            f"- Turnaround time var: {self.var:.2f}"
        )

    # method to set the id to the simulation (it will be the index of the stats 
    # list of class StatsManager
    def set_id(self, id):
        self.id = id

    def set_loss(self, loss):
        self.loss_rate=loss
        self.unreliable=True

    # add the turnaround time to the list
    #   params:
    #       t_time - runtime to add
    def add_runtime(self, t_time):
        self.runtimes.append(t_time)

    # return the list of runtimes
    def get_runtimes(self):
        return self.runtimes

    # computes mean of the runtimes
    def compute_mean(self):
        self.mean = 0
        for el in self.runtimes:
            self.mean += el

        self.mean = self.mean/len(self.runtimes)

    # compute variance of the runtimes
    def compute_var(self):
        self.var = 0
        for el in self.runtimes:
            self.var += ((el - self.mean)**2)

        self.var = self.var/(len(self.runtimes)-1)

    # method to compute asymptotic CI 95% confidence
    def compute_ci(self):
        self.err = 1.96 * math.sqrt(self.var / self.n_nodes)

    # method to plot the histogram of the simulation runtimes
    #   params:
    #       bins - bins of the histogram
    def plot_runtimes_hist(self, bins):
        plt.figure()
        rel = "Unreliable" if self.unreliable else "Reliable"
        title = self.name+" - Simulations with "+rel+" Links"
        plt.title(title)
        plt.hist(self.runtimes, bins=bins)
        plt.xlim()
        plt.xlabel("runtime in ms")
        plt.ylabel("#sim")
        plt.axvline(x = self.mean, color = 'red', label = 'Mean')
        plt.legend()

    def plot_ring_distribution(self, bins):
        plt.figure()
        plt.hist(self.runtimes, bins=bins, label = "Ring - Simulations with Reliable Links", density = True)

        a, loc, scale = st.gamma.fit(self.runtimes, floc=0)
        x = np.linspace(min(self.runtimes), max(self.runtimes), bins)
        y = st.gamma.pdf(x, a, loc = loc, scale=scale)
        plt.plot(x,y, color="red")

        plt.xlim()
        plt.xlabel("Runtime in ms")
        plt.ylabel("Density")
        plt.legend()

    # method to plot the boxplot of the simulation runtimes
    def plot_runtimes_box_plot(self):
        plt.figure()
        plt.boxplot(self.runtimes, tick_labels=[self.name])
        plt.title(self.name+" - Box Plot")
        plt.ylabel("Turnaround Time")
    
    # method to remove outliers datapoints from runtimes
    def remove_outliers(self, whis = 1.5):
        # follows boxplot where outliers are outside the "whiskers"
        q_1 =  np.quantile(self.runtimes, 0.25)
        q_3 = np.quantile(self.runtimes, 0.75)
        bound_1 = q_1 - whis * (q_3 - q_1)
        bound_2 = q_3 + whis * (q_3 - q_1)

        def not_outlier(e):
            if e < bound_1 or e > bound_2:
                return False
            return True

        self.runtimes = list(filter(not_outlier, self.runtimes))


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

    # method to analyze two different simulations' box plots
    #   params:
    #       id1 - index of the first simulation in the stats list
    #       id2 - index of the second simulation in the stats list
    def cmp_runtimes_box_plot(self, id1, id2):
        plt.figure()
        labels=[self.stats[id1].name, self.stats[id2].name]
        plt.boxplot([self.stats[id1].runtimes, self.stats[id2].runtimes], labels=labels)
        plt.title("Box Plots")
        plt.ylabel("Turnaround Time")

    def cmp_runtimes(self, ids, bins, name):

        title = "Simulations Comparison - "+name
        fig, axs = plt.subplots(len(ids))
        fig.suptitle(title)
        
        for i, id in enumerate(ids):
            sim = self.stats[id]

            color = (random.random(), random.random(), random.random())
            sub_label=""
            match name:
                case "Initiators": 
                    sub_label= f"{sim.name} with #initiators={sim.initiators}"
                case "Number of Nodes":
                    sub_label=f"{sim.name} with #nodes={sim.n_nodes}"
                case "Delays Mean":
                    sub_label=f"{sim.name} with delay mean={sim.delay}"
                case "Packet Loss Rate":
                    sub_label=f"{sim.name} with loss rate={sim.loss_rate}"
                case _:
                    sub_label=f"{sim.name}"

            axs[i].hist(sim.runtimes, bins=bins, color=color, label=sub_label)
            axs[i].legend(loc="best")
            axs[i].axvline(x=sim.mean)
    
    def remove_all_outliers(self):
        for i in range(len(self.stats)):
            self.stats[i].remove_outliers()

       