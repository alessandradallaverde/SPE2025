import simpy

from election.ring import RingSimulation
from election.bully import BullySimulation
from statistic.statistics import SimStats, StatsManager
import matplotlib.pyplot as plt

# ------------------- SETTINGS ---------------------
N_NODES = 10
DELAY = 110         # mean of exponential distribution for delays 
INITIATORS = 10
N_SIM = 10000
LOSS = 0.1
UNRELIABLE = False
DELAY_Q = 0.8        # quantile of exponential distribution

sim_manager = StatsManager()
'''
# ------------ RING ALGORITHM SIMULATION ------------
stats_ring = SimStats(INITIATORS, DELAY, N_NODES, "Ring")
stats_ring.set_id(len(sim_manager.stats))
sim_manager.insert_stat(stats_ring)
env_ring = simpy.Environment()
if UNRELIABLE:          #unreliable links
    ring = RingSimulation(env_ring, N_NODES, DELAY, stats_ring, n_initiators=INITIATORS,unreliable=True, loss=LOSS, timeout=DELAY_Q)
    stats_ring.set_loss(LOSS)
else:           #reliable links
    ring = RingSimulation(env_ring, N_NODES, DELAY, stats_ring)          

for i in range(N_SIM):
    env_ring.process(ring.start_election())
    env_ring.run()
    env_ring = simpy.Environment()
    ring.clean(env_ring)            # clean RingSimulation for the next simulation

#stats_ring.remove_outliers()
stats_ring.compute_mean_rtt()
stats_ring.compute_var_rtt()
stats_ring.compute_ci_rtt()

# ANALYZE TURNAROUND TIME
stats_ring.plot_runtimes_hist(200)          # plot histogram of simulations    
stats_ring.plot_runtimes_box_plot()         # plot box plot of simulation

print(stats_ring)           # print simulations results (mean, var, ci)

# ------------ BULLY ALGORITHM SIMULATION -----------
stats_bully = SimStats(INITIATORS, DELAY, N_NODES, "Bully")
if UNRELIABLE:
    stats_bully.set_loss(LOSS)
stats_bully.set_id(len(sim_manager.stats))
sim_manager.insert_stat(stats_bully)
env_bully = simpy.Environment()
bully = BullySimulation(env_bully, N_NODES, DELAY, DELAY_Q, stats_bully)

for i in range (N_SIM):
    if UNRELIABLE:
        bully.env.process(bully.start_election(INITIATORS, loss_rate=LOSS))
    else:
        bully.env.process(bully.start_election(INITIATORS))
    bully.env.run()
    env_bully = simpy.Environment()
    bully.env = env_bully

stats_bully.plot_runtimes_box_plot()
# stats_bully.check_wrong_sim()
stats_bully.remove_outliers()
stats_bully.compute_mean_rtt()
stats_bully.compute_var_rtt()
stats_bully.compute_ci_rtt()
stats_bully.compute_mean_msg()
stats_bully.compute_var_msg()
stats_bully.compute_ci_msg()

# ANALYZE TURNAROUND TIME
stats_bully.plot_runtimes_hist(200)     
stats_bully.plot_runtimes_box_plot()
print(stats_bully)
'''
# ------------ BULLY VS RING -----------
#sim_manager.cmp_runtimes_box_plot(stats_bully.id, stats_ring.id)


# ------------ MULTIFACTORS ANALYSIS -------------

# This method plots different simulations results for different factors
#   params:
#       tot_sims - number of simulations to perform
#       n_init - list containing the number of initiators for each simulation
#       n_n - list containing the number of nodes for each simulation
#       n_delays - list containing the delays' mean for each simulation
#       n_loss - list containing the 1-loss rate for each simulation
#       bully - boolean value, if true the simulations will be the one of the bully
#       unreliable - boolean value, if true we are under the unreliable links assumption
def factors_sim(sim_name, tot_sims, n_init, n_n, n_delays, n_loss, bully, unreliable):
    ids = []            # ids of each pack of simulations in the sim_manager
    mean_rtt = []
    mean_msg = []
    ci_rtt = []
    ci_msg = []
    for i in range(tot_sims):
        # simulations configuration
        name = f"Bully" if bully else f"Ring"
        stats = SimStats(n_init[i], n_delays[i], n_n[i], name)
        if unreliable:
            stats.set_loss(round(1-n_loss[i],2))
        stats.set_id(len(sim_manager.stats))
        sim_manager.insert_stat(stats)
        ids.append(stats.id)

        # core of simulations
        env = simpy.Environment()
        if bully:           # bully simulations
            bully = BullySimulation(env, n_n[i], n_delays[i], DELAY_Q, stats)

            for j in range (N_SIM):
                if unreliable:
                    bully.env.process(bully.start_election(n_init[i], n_loss[i])) 
                else:
                    bully.env.process(bully.start_election(n_init[i]))
                bully.env.run()
                env = simpy.Environment()
                bully.env = env
        else:
            if unreliable:          # ring simulations
                ring = RingSimulation(env, n_n[i], n_delays[i], stats, n_initiators=n_init[i],unreliable=True, loss=n_loss[i], timeout=DELAY_Q)
            else:
                ring = RingSimulation(env, n_n[i], n_delays[i], stats, n_initiators=n_init[i], unreliable=False)

            for j in range(N_SIM):
                env.process(ring.start_election())
                env.run()
                env = simpy.Environment()
                ring.clean(env)

        stats.compute_mean_rtt()
        stats.compute_var_rtt()
        stats.compute_ci_rtt()
        stats.compute_mean_msg()
        stats.compute_var_msg()
        stats.compute_ci_msg()

        mean_rtt.append(stats.mean_rtt)
        mean_msg.append(stats.mean_msg)
        ci_rtt.append(stats.err_rtt)
        ci_msg.append(stats.err_msg)

    mean_rtt = np.array(mean_rtt)
    mean_msg = np.array(mean_msg)
    ci_rtt = np.array(ci_rtt)
    ci_msg = np.array(ci_msg)
    
    #print(mean_rtt, ci_rtt, mean_msg, ci_msg)
    fig, ax = plt.subplots()
    ax.plot(n_n, mean_rtt)
    ax.fill_between(n_n, (mean_rtt-ci_rtt), (mean_rtt+ci_rtt), color='b', alpha=.1)

    fig, ax = plt.subplots()
    ax.plot(n_n, mean_msg)
    ax.fill_between(n_n, (mean_msg-ci_msg), (mean_msg+ci_msg), color='b', alpha=.1)

    #sim_manager.cmp_runtimes(ids, 200, sim_name)            # plot simulations results

tot_sims = 16
sim_title = "Packet Loss Rate"
n_init = [1]*tot_sims
import numpy as np
n_n = np.arange(5, 21, 1, dtype=int)
n_delays = [DELAY]*tot_sims
n_loss = [-1]*tot_sims
factors_sim(sim_title, tot_sims, n_init, n_n, n_delays, n_loss=n_loss, bully=True, unreliable=False)

# ------------ SHOW PLOTS ----------------
plt.show()