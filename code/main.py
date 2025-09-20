import simpy

from election.ring import RingSimulation
from election.bully import BullySimulation
from statistic.statistics import SimStats

# number of nodes in the system
N_NODES = 5

# ------------ RING ALGORITHM SIMULATION ------------

env_ring = simpy.Environment()
ring = RingSimulation(env_ring, N_NODES, 0.15, unreliable=False)
stats_ring = SimStats(1, 0.15, N_NODES)

n_sim = 3
i = 0

while i<n_sim:
    env_ring.process(ring.start_election())
    env_ring.run()

    stats_ring.add_turnaround_time(ring.get_t_time())

    env_ring = simpy.Environment()
    ring.clean(env_ring)

    i+=1

# DEBUG
print(stats_ring.get_t_times())

# ------------ BULLY ALGORITHM SIMULATION -----------

'''
env_bully = simpy.Environment()

bully = BullySimulation(env_bully, N_NODES)
env_bully.process(bully.start_election(2, 0.5))
env_bully.run()
'''