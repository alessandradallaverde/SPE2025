import simpy

from election.ring import RingSimulation
from election.bully import BullySimulation
from statistic.statistics import SimStats

import math
import matplotlib.pyplot as plt

# number of nodes in the system
N_NODES = 5
delay_mean = 110
initiators = 1
n_sim = 20000

# ------------ RING ALGORITHM SIMULATION ------------
ring_stats = SimStats(initiators, delay_mean, N_NODES)
env_ring = simpy.Environment()
ring = RingSimulation(env_ring, N_NODES, delay_mean, ring_stats, unreliable=False)
stats_ring = SimStats(1, 0.15, N_NODES)

'''
for i in range(n_sim):
    env_ring.process(ring.start_election())
    env_ring.run()
    stats_ring.add_turnaround_time(ring.get_t_time())
    env_ring = simpy.Environment()
    ring.clean(env_ring)
'''

# ------------ BULLY ALGORITHM SIMULATION -----------
# simulations with 1 initiator, and 5 nodes
N_NODES = 5
delay_mean = 110
initiators = 1
n_sim = 20000

stats_bully = SimStats(initiators, delay_mean, N_NODES)
env_bully = simpy.Environment()
bully = BullySimulation(env_bully, N_NODES, delay_mean, 0.8, stats_bully)

for i in range (n_sim):
    bully.env.process(bully.start_election(2))
    bully.env.run()
    env_bully = simpy.Environment()
    bully.env = env_bully

# define vars to write clear and concise calls to the statistics method
RTT_STATS = stats_bully.get_rtt_times()
RUNTIME_STATS = stats_bully.get_runtimes()

# 1. Analyze runtimes
# runtimes are distributed according to a skew normal distribution
plt.hist(stats_bully.get_runtimes(), 200)

# asymptotic CI (no wild distribution + large n) 95% confidence
mean = stats_bully.compute_mean(RUNTIME_STATS)
var = stats_bully.compute_var(mean, RUNTIME_STATS)
err = 1.96 * math.sqrt(var / n_sim)

print("Bully Algorithm:")
print("- Simulations: " + str(n_sim))
print("- Parameters: N = %d, init = %d, mean delay = %.2f" % (N_NODES, initiators, delay_mean ))
print("Runtime mean: %.2f \u00B1 %.2f ms" % (mean, err) )
'''
# too slow for a big n
# bootstrap method
bootstrap_ci = stats_bully.bootstrap_stats(0.95, stats_bully.compute_mean, RUNTIME_STATS)
print("Runtime mean with bootstrap method: [%.2f, %.2f]" % (bootstrap_ci[0], bootstrap_ci[1]))
'''

plt.show()
