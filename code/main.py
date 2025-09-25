import simpy

from election.ring import RingSimulation
from election.bully import BullySimulation
from statistic.statistics import SimStats, StatsManager

import math
import matplotlib.pyplot as plt

# ------------------- SETTINGS ---------------------

n_nodes = 5
delay_mean = 110
initiators = 1
n_sim = 10000

sim_manager = StatsManager()

# ------------ RING ALGORITHM SIMULATION ------------
stats_ring = SimStats(initiators, delay_mean, n_nodes, "Ring")
stats_ring.set_id(len(sim_manager.stats))
sim_manager.insert_stat(stats_ring)
env_ring = simpy.Environment()
ring = RingSimulation(env_ring, n_nodes, delay_mean, stats_ring, unreliable=False)

for i in range(n_sim):
    env_ring.process(ring.start_election())
    env_ring.run()
    env_ring = simpy.Environment()
    ring.clean(env_ring)

# 1. ANALYZE TURNAROUND TIME
stats_ring.plot_runtimes_hist(200)     
stats_ring.plot_runtimes_box_plot()

stats_ring.compute_mean()
stats_ring.compute_var()
stats_ring.compute_ci()

print(stats_ring)

# ------------ BULLY ALGORITHM SIMULATION -----------
stats_bully = SimStats(initiators, delay_mean, n_nodes, "Bully")
stats_bully.set_id(len(sim_manager.stats))
sim_manager.insert_stat(stats_bully)
env_bully = simpy.Environment()
bully = BullySimulation(env_bully, n_nodes, delay_mean, 0.8, stats_bully)

for i in range (n_sim):
    bully.env.process(bully.start_election(initiators))
    bully.env.run()
    env_bully = simpy.Environment()
    bully.env = env_bully

# 1. ANALYZE TURNAROUND TIME
stats_bully.plot_runtimes_hist(200)     
stats_bully.plot_runtimes_box_plot()

stats_bully.compute_mean()
stats_bully.compute_var()
stats_bully.compute_ci()

print(stats_bully)

# ------------ BULLY VS RING -----------

sim_manager.cmp_runtimes_box_plot(stats_bully.id, stats_ring.id)

'''
# 3. Analyze loss rates related to runtime
# helper function to not repeat code for runtime mean analysis 
def analyze_mean(loss_rate, sim_manager):
    stats_bully = SimStats(initiators, delay_mean, n_nodes)
    sim_manager.insert_stat(stats_bully)
    env_bully = simpy.Environment()
    bully = BullySimulation(env_bully, n_nodes, delay_mean, 0.8, stats_bully)

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