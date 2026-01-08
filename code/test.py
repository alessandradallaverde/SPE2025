import simpy
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick
from multiprocessing import Pool, cpu_count

from election.bully import BullySimulation
from statistic.statistics import SimStats

# ------------------- SETTINGS ---------------------
N_NODES = 5
DELAY = 110         # mean of exponential distribution for delays 
INITIATORS = 1

# ------------ BULLY TIMEOUT ANALYSIS -------------

def run_single_timeout(t):

    print(f"Running simulation {t}")

    errors = []

    for i in range(500):
        bully_stats = SimStats(INITIATORS, DELAY, N_NODES, "Bully", timeout=t)

        bully_env = simpy.Environment()
        bully_sim = BullySimulation(bully_env, N_NODES, DELAY, t, bully_stats)

        for j in range(1000):
            bully_sim.env.process(bully_sim.start_election(INITIATORS))
            bully_sim.env.run()
            bully_env = simpy.Environment()
            bully_sim.env = bully_env

        bully_stats.wrg_sim()
        errors.append(bully_stats.wrong_stat)

    print(f"End sim {t}")
    mean_err = sum(errors) / len(errors)
    return t, mean_err  

def bully_timeout_analysis_parallel():
    timeouts = np.round(np.arange(0.8, 1.0, 0.01), 2).tolist()
    timeouts.append(0.99)
    timeouts.sort()

    with Pool(processes=cpu_count()) as p:
        results = p.map(run_single_timeout, timeouts)

    res_wrg = dict(results)
    res_wrg = dict(sorted(res_wrg.items()))

    plt.figure()
    plt.title("Bully Wrong Simulations Analysis")
    plt.plot(res_wrg.keys(), res_wrg.values())
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())
    plt.xlabel("Quantile")
    plt.ylabel("Percentage of Wrong Simulations")
    plt.show()

if __name__ == "__main__":
    bully_timeout_analysis_parallel()