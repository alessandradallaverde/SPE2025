import simpy
from election.bully import BullySimulation
from election.ring import RingSimulation
from statistic.statistics import SimStats, StatsManager
import utils

# ------------------- SETTINGS ---------------------
N_NODES = 4
DELAY = 110         # mean of exponential distribution for delays 
INITIATORS = 1
N_SIM = 3
LOSS = 0.5
UNRELIABLE = True
DELAY_Q = 0.7         # quantile of exponential distribution
DEBUG = True

sim_manager = StatsManager()

# ------------ BULLY ALGORITHM SIMULATION -----------
stats_ring = SimStats(INITIATORS, DELAY, N_NODES, "Ring")
stats_ring.set_loss(LOSS)
stats_ring.set_id(len(sim_manager.stats))
sim_manager.insert_stat(stats_ring)
env_ring = simpy.Environment()
max_delay = (2 * utils.max_delay(DELAY_Q, DELAY))
ring = RingSimulation(env_ring, N_NODES, DELAY, stats_ring, n_initiators=INITIATORS,unreliable=True, loss=LOSS, timeout=DELAY_Q, debug_mode=DEBUG)


for i in range (N_SIM):
    ring.env.process(ring.start_election())
    ring.env.run()
    env_ring = simpy.Environment()
    ring.env = env_ring

# ------------ BULLY ALGORITHM SIMULATION -----------
stats_bully = SimStats(INITIATORS, DELAY, N_NODES, "Bully")
stats_bully.set_loss(LOSS)
stats_bully.set_id(len(sim_manager.stats))
sim_manager.insert_stat(stats_bully)
env_bully = simpy.Environment()
bully = BullySimulation(env_bully, N_NODES, DELAY, DELAY_Q, stats_bully)

for i in range (N_SIM):
    if UNRELIABLE:
        bully.env.process(bully.start_election(INITIATORS, loss_rate=LOSS, debug_mode=DEBUG))
    else:
        bully.env.process(bully.start_election(INITIATORS, debug_mode=DEBUG))
    bully.env.run()
    env_bully = simpy.Environment()
    bully.env = env_bully
