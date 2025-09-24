import simpy

from election.ring import RingSimulation
from election.bully import BullySimulation
from statistic.statistics import SimStats, StatsManager

import math
import matplotlib.pyplot as plt

def cmp_runtimes_box_plot(bully_data, ring_data):
    plt.figure()
    labels=["Bully", "Ring"]
    plt.boxplot([bully_data, ring_data], labels=labels)
    plt.title("Box Plot")
    plt.ylabel("Turnaround Times")

# number of nodes in the system
N_NODES = 5
delay_mean = 110
initiators = 1
n_sim = 10000

# ------------ RING ALGORITHM SIMULATION ------------
stats_ring = SimStats(initiators, delay_mean, N_NODES)
env_ring = simpy.Environment()
ring = RingSimulation(env_ring, N_NODES, delay_mean, stats_ring, unreliable=False)

for i in range(n_sim):
    env_ring.process(ring.start_election())
    env_ring.run()
    env_ring = simpy.Environment()
    ring.clean(env_ring)

# 1. ANALYZE TURNAROUND TIME
RUNTIME_STATS_RING = stats_ring.get_runtimes()      # define vars to write clear and concise calls to the statistics' methods

stats_ring.plot_runtimes_hist(200)     # runtimes are distributed according to a skew normal distribution
stats_ring.plot_runtimes_box_plot()

mean = stats_ring.compute_mean(RUNTIME_STATS_RING)
var = stats_ring.compute_var(mean, RUNTIME_STATS_RING)
err = stats_ring.compute_ci()      # asymptotic CI (no wild distribution + large n) 95% confidence

print("Ring Algorithm:")
print("- Simulations: " + str(n_sim))
print("- Parameters: N = %d, init = %d, mean delay = %.2f" % (N_NODES, initiators, delay_mean ))
print("Runtime mean: %.2f \u00B1 %.2f ms" % (mean, err) )

# ------------ BULLY ALGORITHM SIMULATION -----------
# sim_manager = StatsManager()
stats_bully = SimStats(initiators, delay_mean, N_NODES)
# sim_manager.insert_stat(stats_bully)
env_bully = simpy.Environment()
bully = BullySimulation(env_bully, N_NODES, delay_mean, 0.8, stats_bully)

for i in range (n_sim):
    bully.env.process(bully.start_election(initiators))
    bully.env.run()
    env_bully = simpy.Environment()
    bully.env = env_bully

# 1. ANALYZE TURNAROUND TIME
RUNTIME_STATS_BULLY = stats_bully.get_runtimes()      # define vars to write clear and concise calls to the statistics' methods

stats_bully.plot_runtimes_hist(200)     # runtimes are distributed according to a skew normal distribution
stats_bully.plot_runtimes_box_plot()

mean = stats_bully.compute_mean(RUNTIME_STATS_BULLY)
var = stats_bully.compute_var(mean, RUNTIME_STATS_BULLY)
err = stats_bully.compute_ci()      # asymptotic CI (no wild distribution + large n) 95% confidence

print("Bully Algorithm:")
print("- Simulations: " + str(n_sim))
print("- Parameters: N = %d, init = %d, mean delay = %.2f" % (N_NODES, initiators, delay_mean ))
print("Runtime mean: %.2f \u00B1 %.2f ms" % (mean, err) )

cmp_runtimes_box_plot(RUNTIME_STATS_BULLY, RUNTIME_STATS_RING)

'''
# 3. Analyze loss rates related to runtime
# helper function to not repeat code for runtime mean analysis 
def analyze_mean(loss_rate, sim_manager):
    stats_bully = SimStats(initiators, delay_mean, N_NODES)
    sim_manager.insert_stat(stats_bully)
    env_bully = simpy.Environment()
    bully = BullySimulation(env_bully, N_NODES, delay_mean, 0.8, stats_bully)

    for i in range (n_sim):
        bully.env.process(bully.start_election(initiators, loss_rate ))
        bully.env.run()
        env_bully = simpy.Environment()
        bully.env = env_bully

    # define vars to write clear and concise calls to the statistics method
    RUNTIME_STATS = stats_bully.get_runtimes()
    # asymptotic CI (no wild distribution + large n) 95% confidence
    mean = stats_bully.compute_mean(RUNTIME_STATS)
    var = stats_bully.compute_var(mean, RUNTIME_STATS)
    err = 1.96 * math.sqrt(var / n_sim)

    # weird distribution
    print("- With unreliable loss rate: %.2f" % loss_rate )
    print("Runtime mean: %.2f \u00B1 %.2f ms" % (mean, err) )
    plt.figure()
    plt.hist(RUNTIME_STATS, 200, label = "Simulations with loss_rate {lr: .2f}".format(lr = loss_rate))
    plt.xlabel("Runtime in ms")
    plt.legend()

# simulations with different loss_rates
analyze_mean(0.2, sim_manager)
analyze_mean(0.5, sim_manager)
analyze_mean(0.8, sim_manager)
'''

plt.show()