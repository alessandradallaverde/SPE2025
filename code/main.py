import simpy
import matplotlib.pyplot as plt
import numpy as np
import time

from election.ring import RingSimulation
from election.bully import BullySimulation
from statistic.statistics import SimStats, StatsManager

# ------------------- SETTINGS ---------------------
# DEFAULT SCENARIO
N_NODES = 5
DELAY = 110         # mean of exponential distribution for delays 
INITIATORS = 1
N_SIM = 10000
LOSS = 0.2      
DELAY_Q_R = 0.99       # quantile of exponential distribution for reliable Bully timeouts  
DELAY_Q = 0.8           # quantile of exponential distribution for unreliable timeouts

sim_manager = StatsManager()

# ------------ RING ALGORITHM SIMULATION ------------

# This function generates the SimStats for one simulation
#   params:
#       initiators - number of initiators
#       delay - exponential mean for delays
#       n_nodes - number of nodes
#       unreliable - boolean value, if true the simulations are under unreliable links
#       loss - loss rate
#       delay_q - quantile of exponential distribution for unreliable timeouts
def set_stats(initiators, delay, n_nodes, name, unreliable = False, loss = 0.0, delay_q = 0.0):
    stats = SimStats(initiators, delay, n_nodes, name, unreliable, delay_q, loss)
    stats.set_id(len(sim_manager.stats))
    sim_manager.insert_stat(stats)

    return stats

# This function perform a Ring algorithm simulation
#   params:
#       stats_ring - SimStats of the Ring algorithm simulations
#       n_nodes - number of nodes
#       delay - exponential mean for delays
#       initiators - number of initiators
#       n_sim - number of repetitions of the Ring procedure
#       unreliable - boolean value, if true the simulations are under unreliable links
#       loss - loss rate
#       timeout - quantile of exponential distribution for unreliable timeouts
def ring_sim(stats_ring, n_nodes, delay, initiators, n_sim, unreliable = False,
               loss = 0.0, timeout = 0.0, debug_mode=False):

    env_ring = simpy.Environment()
    if unreliable:          
        ring = RingSimulation(env_ring, n_nodes, delay, stats_ring, n_initiators=initiators,
                                unreliable=True, loss=loss, timeout=timeout, debug_mode=debug_mode)
    else:          
        ring = RingSimulation(env_ring, n_nodes, delay, stats_ring, n_initiators=initiators)          

    for i in range(n_sim):
        env_ring.process(ring.start_election())         # starts Ring procedure
        env_ring.run()
        env_ring = simpy.Environment()
        ring.clean(env_ring)            

    # statistics computation
    stats_ring.remove_outliers()
    stats_ring.compute_mean_rtt()
    stats_ring.compute_var_rtt()
    stats_ring.compute_ci_rtt()
    stats_ring.compute_mean_msg()
    stats_ring.compute_var_msg()
    stats_ring.compute_ci_msg()

# SINGLE RUN RELIABLE LINKS
print("------------------------------------------------\n")
print("---------SINGLE RUN RING RELIABLE LINKS---------\n")

stats_ring = set_stats(INITIATORS, DELAY, N_NODES, "Ring", False, LOSS, DELAY_Q)
env_ring = simpy.Environment()
ring = RingSimulation(env_ring, N_NODES, DELAY, stats_ring, n_initiators=INITIATORS, debug_mode=True)          
env_ring.process(ring.start_election())         # starts Ring procedure
env_ring.run()  
print("\nRing election algorithm terminated")
print("\n------------------------------------------------\n")     

# RELIABLE LINKS
print("-------------- RING RELIABLE LINKS-------------\n")
print("------------------------------------------------\n\n")

stats_ring = set_stats(INITIATORS, DELAY, N_NODES, "Ring", False, LOSS, DELAY_Q)
print("Starting ring with reliable links execution...\n")
ring_sim(stats_ring, N_NODES, DELAY, INITIATORS, N_SIM, False, LOSS, DELAY_Q)
print("Election completed!\n\n")

# stats_ring.plot_ring_distribution(200)      # plot histogram of turnaround times (density)
stats_ring.plot_runtimes_hist(200)          # plot histogram of turnaround times 
print(stats_ring)           # print simulations results 
plt.show()

# SINGLE RUN UNRELIABLE LINKS
print("------------------------------------------------\n")
print("--------SINGLE RUN RING UNRELIABLE LINKS--------\n")

stats_ring = set_stats(INITIATORS, DELAY, N_NODES, "Ring", True, LOSS, DELAY_Q)
env_ring = simpy.Environment()
ring = RingSimulation(env_ring, N_NODES, DELAY, stats_ring, n_initiators=INITIATORS,
                       unreliable=True, timeout=DELAY_Q, loss=LOSS, debug_mode=True)          
env_ring.process(ring.start_election())         # starts Ring procedure
env_ring.run()       
print("\nRing election algorithm terminated")
print("\n------------------------------------------------\n")

# UNRELIABLE LINKS
print("-------------RING UNRELIABLE LINKS--------------\n")
print("------------------------------------------------\n\n")

stats_ring = set_stats(INITIATORS, DELAY, N_NODES, "Ring", True, LOSS, DELAY_Q)
print("Starting ring with unreliable links execution...\n")
ring_sim(stats_ring, N_NODES, DELAY, INITIATORS, N_SIM, True, LOSS, DELAY_Q)
print("Simulation completed!\n\n")

stats_ring.plot_runtimes_hist(200)          # plot histogram of turnaround times 
print(stats_ring)           # print simulations results 
plt.show()

# ------------ BULLY ALGORITHM SIMULATION -----------
# This function perform a Bully algorithm simulation
#   params:
#       stats_bully - SimStats of the Bully algorithm simulations
#       n_nodes - number of nodes
#       delay - exponential mean for delays
#       initiators - number of initiators
#       n_sim - number of repetitions of the Ring procedure
#       unreliable - boolean value, if true the simulations are under unreliable links
#       loss - loss rate
#       delay_q - quantile of exponential distribution for unreliable timeouts
#       delay_q_r - quantile of exponential distribution for reliable timeouts
def bully_sim(stats_bully, n_nodes, delay, initiators, n_sim, unreliable = False, 
               loss = 0.0, delay_q = 0.0, delay_q_r = 0.0, debug_mode = False):
    
    env_bully = simpy.Environment()
    if unreliable:
        bully = BullySimulation(env_bully, n_nodes, delay, delay_q, stats_bully)
    else:
        bully = BullySimulation(env_bully, n_nodes, delay, delay_q_r, stats_bully)

    for i in range (n_sim):
        if unreliable:          # Bully procedure
            bully.env.process(bully.start_election(initiators, loss_rate=loss, debug_mode=debug_mode))
        else:
            bully.env.process(bully.start_election(initiators, debug_mode=debug_mode))
        bully.env.run()
        env_bully = simpy.Environment()
        bully.env = env_bully

    # statistics computation
    stats_bully.wrg_sim()
    stats_bully.remove_outliers()
    stats_bully.compute_mean_rtt()
    stats_bully.compute_var_rtt()
    stats_bully.compute_ci_rtt()
    stats_bully.compute_mean_msg()
    stats_bully.compute_var_msg()
    stats_bully.compute_ci_msg()

# SINGLE RUN RELIABLE LINKS
print("------------------------------------------------\n")
print("---------SINGLE RUN BULLY RELIABLE LINKS--------\n")

stats_bully = set_stats(INITIATORS, DELAY, N_NODES, "Bully", False, LOSS, DELAY_Q_R)
env_bully = simpy.Environment()
bully = BullySimulation(env_bully, N_NODES, DELAY, DELAY_Q_R, stats_bully)
bully.env.process(bully.start_election(INITIATORS, debug_mode=True))
bully.env.run()

# RELIABLE LINKS 
print("--------------BULLY RELIABLE LINKS--------------\n")
print("------------------------------------------------\n\n")
stats_bully = set_stats(INITIATORS, DELAY, N_NODES, "Bully", False, LOSS, DELAY_Q_R)
print("Starting bully with reliable links execution...\n")
bully_sim(stats_bully, N_NODES, DELAY, INITIATORS, N_SIM, False, LOSS, DELAY_Q, DELAY_Q_R)
print("Simulation completed!\n\n")

stats_bully.plot_runtimes_hist(200)         # plot histogram of turnaround times   
print(stats_bully)
plt.show()

# SINGLE RUN UNRELIABLE LINKS

print("------------------------------------------------\n")
print("--------SINGLE RUN BULLY UNRELIABLE LINKS-------\n")

stats_bully = set_stats(INITIATORS, DELAY, N_NODES, "Bully", True, LOSS, DELAY_Q)
env_bully = simpy.Environment()
bully = BullySimulation(env_bully, N_NODES, DELAY, DELAY_Q, stats_bully)
bully.env.process(bully.start_election(INITIATORS, loss_rate=LOSS, debug_mode=True))
bully.env.run()

# UNRELIABLE LINKS
print("-------------BULLY UNRELIABLE LINKS-------------\n")
print("------------------------------------------------\n\n")
print(LOSS, DELAY_Q)
stats_bully = set_stats(INITIATORS, DELAY, N_NODES, "Bully", True, LOSS, DELAY_Q)
print("Starting bully with unreliable links execution...\n")
bully_sim(stats_bully, N_NODES, DELAY, INITIATORS, N_SIM, True, LOSS, DELAY_Q, DELAY_Q_R)
print("Simulation completed!\n\n")

stats_bully.plot_runtimes_hist(200)         # plot histogram of turnaround times   
print(stats_bully)
plt.show()

# ------------ BULLY VS RING -----------

sim_manager.cmp_runtimes_box_plot(stats_bully.id, stats_ring.id)        # plot Ring and Bully of turnaround times box plot
plt.show()

# ------------ FACTORS ANALYSIS -------------

# This function plots different simulations results for different factors
#   params:
#       sim_name - name of the simulations
#       tot_sims - number of simulations to perform
#       n_init - list containing the number of initiators for each simulation
#       n_n - list containing the number of nodes for each simulation
#       n_delays - list containing the delays' mean for each simulation
#       n_loss - list containing the loss rate for each simulation
#       bully - boolean value, if true the simulations will be the one of the bully
#       unreliable - boolean value, if true we are under the unreliable links assumption
def factors_sim(sim_name, tot_sims, n_init, n_n, n_delays, n_loss, bully, unreliable):
    ids = []            # ids of each pack of simulations in the sim_manager

    for i in range(tot_sims):
        # set SimStats
        name = f"Bully" if bully else f"Ring"
        if bully and not unreliable:
            stats = set_stats(n_init[i], n_delays[i], n_n[i], name, unreliable, n_loss[i], DELAY_Q_R)
        else:
            stats = set_stats(n_init[i], n_delays[i], n_n[i], name, unreliable, n_loss[i], DELAY_Q)
        ids.append(stats.id)

        # perform simulations
        if bully:
            bully_sim(stats, n_n[i], n_delays[i], n_init[i], N_SIM, unreliable, n_loss[i], DELAY_Q, DELAY_Q_R)
        else:
            ring_sim(stats, n_n[i], n_delays[i], n_init[i], N_SIM, unreliable, n_loss[i], DELAY_Q)

        match sim_name:
            case "Initiators": 
                print(f"Completed simulation with #initiators = {n_init[i]}\n")
            case "Number of Nodes":
                print(f"Completed simulation with #nodes = {n_n[i]}\n")
            case "Delays Mean":
                print(f"Completed simulation with delay mean = {n_delays[i]}\n")
            case "Packet Loss Rate":
                print(f"Completed simulation with loss rate = {n_loss[i]}\n")
            case _:
                print(f"Completed simulation {i}")

    sim_manager.cmp_runtimes(ids, 200, sim_name)            # plot simulations results

# possible titles to obtain a right plot
#   - "Initiators" -> if the number of initiators changes
#   - "Number of Nodes" -> if the number of nodes changes
#   - "Delays Mean" -> if the delay mean changes
#   - "Packet Loss Rate" -> if the packet loss changes
tot_sims = 3
sim_title = "Packet Loss Rate"
n_init = [1]*tot_sims
n_n = [5]*tot_sims
n_delays = [DELAY]*tot_sims
n_loss = [0.2, 0.5, 0.75]

print("------------------------------------------------\n")
print("-------------BULLY LOSS RATE ANALYSIS-----------\n")
print("------------------------------------------------\n\n")

print("Starting bully loss rate analysis...\n")
factors_sim(sim_title, tot_sims, n_init, n_n, n_delays, n_loss=n_loss, bully=True, unreliable=True)
print("Analysis completed!\n\n")
plt.show()

# ------------ NUMBER OF NODES ANALYSIS -------------

# This function plots the number of messages and the turnaround time at the 
# variation of the number of nodes
#   params:
#       max_n_nodes - maximum number of nodes 
#       bully - if true, simulations refer to the Bully, Ring otherwise
#       unreliable - if true, simulations under unreliable links
def n_nodes_sim(max_n_nodes, bully = True, unreliable = False):
    ids = []            # ids of each pack of simulations in the sim_manager

    if max_n_nodes < 3: return 

    for i in range(3, max_n_nodes):
        name = f"Bully" if bully else f"Ring"
        if bully and not unreliable:
            stats = set_stats(1, DELAY, i, name, unreliable, round(LOSS, 2), DELAY_Q_R)
        else:
            stats = set_stats(1, DELAY, i, name, unreliable, round(LOSS, 2), DELAY_Q)
        ids.append(stats.id)

        if bully:
            bully_sim(stats, i, DELAY, 1, N_SIM, unreliable,round(LOSS, 2), DELAY_Q, DELAY_Q_R)
        else:
            ring_sim(stats, i, DELAY, 1, N_SIM, unreliable, round(LOSS, 2), DELAY_Q)
        print(f"Completed simulation with #nodes = {i}\n")

    sim_manager.n_nodes_cmp(ids)
    print("\n")

print("------------------------------------------------\n")
print("-------------NUMBER OF NODES ANALYSIS-----------\n")
print("------------------------------------------------\n\n")

print("Starting number of nodes analysis of the bully reliable links...\n")
# n_nodes_sim(25, bully=True, unreliable=False)
plt.show()
print("Starting number of nodes analysis of the ring reliable links...\n")
# n_nodes_sim(25, bully=False, unreliable=False)
plt.show()
print("Starting number of nodes analysis of the bully unreliable links...\n")
# n_nodes_sim(25, bully=True, unreliable=True)
plt.show()
print("Starting number of nodes analysis of the ring unreliable links...\n")
# n_nodes_sim(25, bully=False, unreliable=True)
plt.show()
print("Analysis completed!\n\n")

# ------------ RELIABLE BULLY TIMEOUTS ANALYSIS -------------

# This function compare the mean of the number of messages and the turnaround 
# time mean of the reliable Bully algorithm for different timeouts quantile 
def bully_timeout_analysis():

    timeouts = np.round(np.arange(0.8, 1.0, 0.01), 2).tolist()      # generate timeouts quantiles from 0.8 to 0.98  
    timeouts.sort()

    ids = []            # ids of each pack of simulations in the sim_manager

    for t in timeouts:
        # Bully simulation
        bully_stats = set_stats(INITIATORS, DELAY, N_NODES, "Bully", unreliable=False, loss=LOSS, delay_q=t)
        ids.append(bully_stats.id)
        bully_sim(bully_stats, N_NODES, DELAY, INITIATORS, N_SIM, unreliable= False, loss=round(LOSS, 2),delay_q= DELAY_Q, delay_q_r=t)
        print(f"Completed simulation with quantile = {t}\n")
    
    sim_manager.quantile_bully_cmp(ids)

print("------------------------------------------------\n")
print("----------BULLY RELIABLE LINKS ANALYSIS---------\n")
print("------------------------------------------------\n\n")

print("Starting bully reliable links turnaround time analysis...\n")
bully_timeout_analysis()
print("Analysis completed")
plt.show()