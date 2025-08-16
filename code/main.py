from node.ring_node import RingNode
from election.ring import RingSimulation
from election.bully import BullySimulation
import simpy

# number of nodes in the system
N_NODES = 5

# ------------ RING ALGORITHM SIMULATION ------------

env_ring = simpy.Environment()

ring = RingSimulation(env_ring, N_NODES, False, 0.15)
env_ring.process(ring.start_election())
env_ring.run()

# DEBUG
print("\nRing election algorithm terminated")
print("\n------------------------------------------------\n")

# ------------ BULLY ALGORITHM SIMULATION -----------

env_bully = simpy.Environment()

bully = BullySimulation(env_bully, N_NODES)
env_bully.process(bully.start_election(3))
env_bully.run()