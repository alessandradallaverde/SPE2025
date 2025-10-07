import simpy

from election.ring import RingSimulation
from election.bully import BullySimulation
from statistic.statistics import SimStats, StatsManager

import math
import matplotlib.pyplot as plt

# ------------------- SETTINGS ---------------------
n_nodes = 4
delay = 110
initiators = 1
n_sim = 10000
loss = 0.8

sim_manager = StatsManager()

# ------------ RING ALGORITHM SIMULATION ------------
stats_ring = SimStats(initiators, delay, n_nodes, "Ring")
stats_ring.set_id(len(sim_manager.stats))
sim_manager.insert_stat(stats_ring)
env_ring = simpy.Environment()
ring = RingSimulation(env_ring, n_nodes, delay, stats_ring)          # reliable links
# ring = RingSimulation(env_ring, n_nodes, delay, stats_ring, n_initiators=initiators,unreliable=True, loss=0.8, timeout=delay)

for i in range(n_sim):
    env_ring.process(ring.start_election())
    env_ring.run()
    env_ring = simpy.Environment()
    ring.clean(env_ring)

stats_ring.compute_mean()
stats_ring.compute_var()
stats_ring.compute_ci()

# ANALYZE TURNAROUND TIME
stats_ring.plot_runtimes_hist(200)     
stats_ring.plot_runtimes_box_plot()

print(stats_ring)

# ------------ BULLY ALGORITHM SIMULATION -----------
stats_bully = SimStats(initiators, delay, n_nodes, "Bully")
stats_bully.set_id(len(sim_manager.stats))
sim_manager.insert_stat(stats_bully)
env_bully = simpy.Environment()
bully = BullySimulation(env_bully, n_nodes, delay, 0.8, stats_bully)

for i in range (n_sim):
    #bully.env.process(bully.start_election(initiators))         #reliable
    bully.env.process(bully.start_election(initiators, loss_rate=loss))         #unreliable
    bully.env.run()
    env_bully = simpy.Environment()
    bully.env = env_bully

stats_bully.compute_mean()
stats_bully.compute_var()
stats_bully.compute_ci()

# ANALYZE TURNAROUND TIME
# stats_bully.plot_runtimes_hist(200)     
# stats_bully.plot_runtimes_box_plot()

print(stats_bully)

# ------------ BULLY VS RING -----------

sim_manager.cmp_runtimes_box_plot(stats_bully.id, stats_ring.id)

# ------------ MULTIFACTORS ANALYSIS -------------

# This method plots different simulations results for different factors
#   params:
#       tot_sims - number of simulations to perform
#       n_init - list containing the number of initiators for each simulation
#       n_n - list containing the number of nodes for each simulation
#       n_delays - list containing the delays' mean for each simulation
#       bully - boolean value, if true the simulations will be the one of the bully
#       unreliable - boolean value, if true we are under the unreliable links assumption
# TODO: manage unreliable links
# TODO: add n_loss_rate
def factors_sim(sim_name, tot_sims, n_init, n_n, n_delays, bully, unreliable):
    ids = []

    for i in range(tot_sims):
        name = f"Bully" if bully else f"Ring"
        stats = SimStats(n_init[i], n_delays[i], n_n[i], name)
        stats.set_id(len(sim_manager.stats))
        sim_manager.insert_stat(stats)
        ids.append(stats.id)

        env = simpy.Environment()
        if bully:
            bully = BullySimulation(env, n_n[i], n_delays[i], 0.8, stats)

            for j in range (n_sim):
                bully.env.process(bully.start_election(n_init[i]))
                bully.env.run()
                env = simpy.Environment()
                bully.env = env
        else:
            ring = RingSimulation(env, n_n[i], n_delays[i], stats, unreliable=False)

            for j in range(n_sim):
                env.process(ring.start_election())
                env.run()
                env = simpy.Environment()
                ring.clean(env)

        stats.compute_mean()
        stats.compute_var()
        stats.compute_ci()

    sim_manager.cmp_runtimes(ids, 200, sim_name)

tot_sims = 3
sim_title = "Delays Mean"
n_init = [initiators]*tot_sims
n_n = [n_nodes]*tot_sims
n_delays = [55, 110, 220]

factors_sim(sim_title, tot_sims, n_init, n_n, n_delays, bully=True, unreliable=False)

# ------------ SHOW PLOTS ----------------
plt.show()


'''
# 3. Analyze loss rates related to runtime
# helper function to not repeat code for runtime mean analysis 
def analyze_mean(loss_rate, sim_manager):
    stats_bully = SimStats(initiators, delay, n_nodes)
    sim_manager.insert_stat(stats_bully)
    env_bully = simpy.Environment()
    bully = BullySimulation(env_bully, n_nodes, delay, 0.8, stats_bully)

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