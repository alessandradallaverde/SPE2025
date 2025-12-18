import math
from numpy import random 
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
from collections import Counter


# this class represents the statistics for multiple simulations of an election
# algorithm with the same factors
#
#   attributes:
#       initiators - number of initiators
#       delay - delay (exponential mean) chosen for the simulation
#       n_nodes - number of nodes in the net
#       name - name of the simulation
#       unreliable - if true, the simulation assumes unreliable links
#       timeout - quantile of exponential distribution to set the timeout
#       loss_rate - prob. that a message isn't received under unreliable links condition
#       runtimes - list containing runtime/turnaround time for each simulation
#       msg_counter - list of the number of messages
#       id - id of the simulation
#       current_sim - number of the algorithm execution
#       mean_rtt - mean of the runtimes
#       mean_msg - mean of the number of messages 
#       var_rtt - var of the runtimes
#       var_msg - var of the number of messages
#       err_rtt - err of the runtimes
#       err_msg - err of the number of messages
#       self.wrong_sims - list of runtimes of wrong simulations (only for reliable bully)
class SimStats:
    def __init__(self, initiators, delay, n_nodes, name, unreliable = False, timeout=0.0, loss_rate=0.0):
        self.initiators = initiators
        self.delay = delay
        self.n_nodes = n_nodes
        self.name = name
        self.unreliable = unreliable
        self.timeout = timeout
        self.loss_rate = loss_rate
        
        self.runtimes = []
        self.msg_counter = []
        self.delays_hist = []
        self.delays = []
        self.id = -1

        self.mean_rtt = 0
        self.mean_msg = 0
        self.var_rtt = 0
        self.var_msg = 0
        self.err_rtt = 0
        self.err_msg = 0

        # for bully simulation in the reliable case: identify which simulations are "wrong"
        self.wrong_sims = []
        self.wrong_stat = 0.0

    def __str__(self):
        main_info = (
            f"{self.name} Algorithm:\n"
            f"- Simulations: {len(self.runtimes)}\n"
            f"- Parameters: N = {self.n_nodes}, init = {self.initiators}, mean delay = {self.delay:.2f}\n"
            f"- Turnaround time mean: {self.mean_rtt:.2f} \u00B1 {self.err_rtt:.2f} ms\n"
            f"- Turnaround time var: {self.var_rtt:.2f}\n"
            f"- Message number mean: {self.mean_msg:.2f} \u00B1 {self.err_msg:.2f}\n"
            f"- Message number var: {self.var_msg:.2f}\n"
        )
        
        if self.name == "Bully" and not self.unreliable:
            main_info += f"- Wrong simulations: {self.wrong_stat:.4f} %"

        return main_info
    
    # method to return the list of runtimes
    def get_runtimes(self):
        return self.runtimes

    # method to set the id to the simulation (it will be the index of the stats 
    # list of class StatsManager
    def set_id(self, id):
        self.id = id

    # method to set the loss rate
    #   params:
    #       loss - loss rate
    def set_loss(self, loss):
        self.loss_rate=loss
        self.unreliable=True

    # method to set the timeout
    #   params:
    #       timeout - quantile of exponential distribution to set the timeout
    def set_timeout(self, timeout):
        self.timeout = timeout

    # add the turnaround time to the list
    #   params:
    #       t_time - runtime to add
    def add_runtime(self, t_time):
        self.runtimes.append(t_time)

    # increase counter message
    #   params:
    #       id - simulation index
    def add_msg(self, id, delay):
        if id == len(self.msg_counter):
            self.msg_counter.insert(id, 0)
        self.msg_counter[id] += 1
        self.delays.append(delay)

    # method to clear delays list and save histogram information
    def clear_delays(self, sim_id=-1):
        if sim_id < len(self.msg_counter) and sim_id >= 0:
            # TODO: decide how to set the bins
            bins_msg = round(self.msg_counter[sim_id]/2)        

            counts, bins = np.histogram(self.delays, bins=bins_msg)
            counts_d, bins_d = np.histogram(self.delays, bins=bins_msg, density=True)
            self.delays_hist.append((counts, bins, counts_d, bins_d))         

            self.delays.clear()     # clear the delays list for the next simulation


    # add index of simulation to the wrong simulations counter
    def add_wrong_sim(self):
        self.wrong_sims.append(len(self.runtimes))

    # method to check the rate of wrong simulations of the reliable bully
    def check_wrong_sim(self, whis = 1.5):
        # follows boxplot where outliers are outside the "whiskers"
        q_1 =  np.quantile(self.runtimes, 0.25)
        q_3 = np.quantile(self.runtimes, 0.75)
        bound_1 = q_1 - whis * (q_3 - q_1)
        bound_2 = q_3 + whis * (q_3 - q_1)

        wrong_outlier = 0
        for w_s in self.wrong_sims:
            if self.runtimes[w_s] < bound_1 or self.runtimes[w_s] > bound_2:
                wrong_outlier += 1
        
        print ( (wrong_outlier/len(self.wrong_sims))*100, " of wrong simulations are also outliers")
        
    def wrg_sim(self):
        if self.name == "Bully" and not self.unreliable:
            self.wrong_stat = (len(self.wrong_sims) / len(self.runtimes)) * 100

    # computes mean of runtimes
    def compute_mean_rtt(self):
        self.mean_rtt = self.compute_mean(self.runtimes)

    # computes mean of number of messages
    def compute_mean_msg(self):
        self.mean_msg = self.compute_mean(self.msg_counter)

    # computes mean
    #   params:
    #       stat_arr - reference to array to compute the mean of
    def compute_mean(self, stat_arr):
        mean = 0
        for el in stat_arr:
            mean += el

        return mean/len(stat_arr)

    # computes variance of runtimes
    def compute_var_rtt(self):
        self.var_rtt = self.compute_var(self.runtimes, self.mean_rtt)

    # computes variance of number of messages
    def compute_var_msg(self):
        self.var_msg = self.compute_var(self.msg_counter, self.mean_msg)

    # compute variance
    #   params:
    #       stat_arr  - reference to array to compute the variance of
    #       stat_mean - mean of given array
    def compute_var(self, stat_arr, stat_mean):
        var = 0
        for el in stat_arr:
            var += ((el - stat_mean)**2)

        return var/(len(stat_arr)-1)
    
    # method to compute asymptotic CI 95% confidence for runtimes
    def compute_ci_rtt(self):
        self.err_rtt = self.compute_ci(self.var_rtt, len(self.runtimes))

    # method to compute asymptotic CI 95% confidence for number of messages
    def compute_ci_msg(self):
        self.err_msg = self.compute_ci(self.var_msg, len(self.msg_counter))

    # method to compute asymptotic CI 95% confidence
    #   params:
    #       var       - variance of array to compute ci for
    #       n         - length of array to compute ci for
    def compute_ci(self, var, n):
        return 1.96 * math.sqrt(var / n)

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
        plt.xlabel("Turnaround Time [ms]")
        plt.ylabel("#sim")
        plt.axvline(x = self.mean_rtt, color = 'red', label = 'Mean')
        plt.legend()

    # method to plot the histogram of the simulation runtimes and the gamma 
    # distribution 
    def plot_ring_distribution(self, bins):
        plt.figure()
        plt.hist(self.runtimes, bins=bins, label = "Ring - Simulations with Reliable Links", density = True)

        a, loc, scale = st.gamma.fit(self.runtimes, floc=0)
        x = np.linspace(min(self.runtimes), max(self.runtimes), bins)
        y = st.gamma.pdf(x, a, loc = loc, scale=scale)
        plt.plot(x,y, color="red")

        plt.xlim()
        plt.xlabel("Turnaround Time [ms]")
        plt.ylabel("Density")
        plt.legend()

    # method to plot the boxplot of the simulation runtimes
    def plot_runtimes_box_plot(self):
        plt.figure()
        plt.boxplot(self.runtimes, tick_labels=[self.name])
        plt.title(self.name+" - Box Plot")
        plt.ylabel("Turnaround Time [ms]")

    # method to plot the histogram of the delays for a given simulation
    #   params:
    #       sim_index - index of the simulation
    #       density - if true, it plots the density
    def plot_delays_hist_single(self, sim_index, density = False):
        if sim_index >= len(self.delays_hist): return     

        plt.figure()
        if density:
            plt.stairs(self.delays_hist[sim_index][2], self.delays_hist[sim_index][3])
            plt.title(self.name+" - Delays Histogram")
            plt.ylabel("Count")
        else:
            plt.stairs(self.delays_hist[sim_index][0], self.delays_hist[sim_index][1])
            plt.title(self.name+" - Delays Density")
            plt.ylabel("Density")

        plt.xlabel("Delay")

    def plot_msg_vs_rtt(self, sim_index, bins):
        title = self.name+" - Msg vs. Runtime"
        fig, axs = plt.subplots(1,2)
        fig.suptitle(title)
        
        axs[0].hist(self.runtimes, bins=bins)
        rel = "Unreliable" if self.unreliable else "Reliable"
        axs[0].set_title(self.name+" - "+rel+" Links")
        axs[0].set_xlabel("Runtime [ms]")
        axs[0].set_ylabel("#sim")

        counts = Counter(self.msg_counter)
        counts = dict(sorted(counts.items()))
        axs[1].plot(counts.keys(), counts.values(), linestyle='dotted')
        axs[1].set_title(self.name+" - Msg Histogram")
        axs[1].set_xlabel("#msg")
        axs[1].set_ylabel("Counts")
    
    # method to remove outliers data points from runtimes and msg 
    def remove_outliers(self, whis = 1.5):
        # follows boxplot where outliers are outside the "whiskers"

        if len(self.runtimes) == 0:
            print("Warning: no runtimes available to remove outliers.")
            return
        q_1 =  np.quantile(self.runtimes, 0.25)
        q_3 = np.quantile(self.runtimes, 0.75)
        bound_1 = q_1 - whis * (q_3 - q_1)
        bound_2 = q_3 + whis * (q_3 - q_1)

        def not_outlier(e):
            if e < bound_1 or e > bound_2:
                return False
            return True

        self.runtimes = list(filter(not_outlier, self.runtimes))

        q_1 =  np.quantile(self.msg_counter, 0.25)
        q_3 = np.quantile(self.msg_counter, 0.75)
        bound_1 = q_1 - whis * (q_3 - q_1)
        bound_2 = q_3 + whis * (q_3 - q_1)
        self.msg_counter = list(filter(not_outlier, self.msg_counter))

    '''
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
    '''

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
    
    # method to show different simulations runtimes based on the factor that 
    # changed
    #   params:
    #       ids - index of the simulation contained in the stats attribute
    #       bins - number of the bins for the histogram
    #       name - title of the simulation comparison
    def cmp_runtimes(self, ids, bins, name):

        reliable = "Unreliable" if self.stats[ids[0]].unreliable else "Reliable"
        title = reliable + " " +self.stats[ids[0]].name+ " Analysis - "+name
        fig, axs = plt.subplots(len(ids), sharex = True)
        fig.suptitle(title)
        
        for i, id in enumerate(ids):
            sim = self.stats[id]

            color = (random.random(), random.random(), random.random())
            sub_label=""
            match name:
                case "Initiators": 
                    sub_label= f"#initiators={sim.initiators}"
                case "Number of Nodes":
                    sub_label=f"#nodes={sim.n_nodes}"
                case "Delays Mean":
                    sub_label=f"delay mean={sim.delay}"
                case "Packet Loss Rate":
                    sub_label=f"loss rate={sim.loss_rate}"
                case _:
                    sub_label=f"{sim.name}"

            axs[i].hist(sim.runtimes, bins=bins, color=color, label=sub_label)
            axs[i].legend(loc="best")
            axs[i].axvline(x=sim.mean_rtt)

    def n_nodes_cmp(self, ids):

        res_rtt = {}   
        res_msg = {}

        for id in ids:
            sim = self.stats[id]
            res_rtt[sim.n_nodes] = sim.mean_rtt
            res_msg[sim.n_nodes] = sim.mean_msg

        rel = "Unreliable" if self.stats[ids[0]].unreliable else "Reliable"
        title = "Number of Nodes Analysis - " + self.stats[ids[0]].name + " with " + rel + " Links"
        fig, axs = plt.subplots(1,2)
        fig.suptitle(title)
        
        res_rtt = dict(sorted(res_rtt.items()))
        axs[0].plot(res_rtt.values(), res_rtt.keys())
        axs[0].set_title("Turnaround Time vs. #nodes")
        axs[0].set_xlabel("Turnaround Time [ms]")
        axs[0].set_ylabel("#nodes")

        res_msg = dict(sorted(res_msg.items()))
        axs[1].plot(res_msg.values(), res_msg.keys())
        axs[1].set_title("#msg vs. #nodes")
        axs[1].set_xlabel("#msg")
        axs[1].set_ylabel("#nodes")

    def quantile_bully_cmp(self, ids):
        res_rtt = {}   

        for id in ids:
            sim = self.stats[id]
            res_rtt[sim.timeout] = sim.mean_rtt

        res_rtt = dict(sorted(res_rtt.items()))
        plt.figure()
        plt.title("Bully Wrong Simulations Analysis")
        plt.plot(res_rtt.keys(), res_rtt.values())
        plt.xlabel("Quantile")
        plt.ylabel("Turnaround Time [ms]")