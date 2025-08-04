from node import RingNode
from ring import RingSimulation
from bully import BullySimulation
import simpy

# ------------ RING ALGORITHM SIMULATION ------------

# number of nodes in the system
N_NODES = 5

# create simpy environment
env = simpy.Environment()

# process that runs both simulations
def run_both_sim():
    # create nodes with IDs i = 0, 1, 2, ...
    ring_nodes = []
    for i in range(N_NODES):
        ring_nodes.append(RingNode(env,i))

    # pass the peers to the nodes
    for i in range(N_NODES):
        ring_nodes[i].obtain_peers(ring_nodes)

    # create simulation class
    ring = RingSimulation(env, ring_nodes, False)
    bully = BullySimulation(env, N_NODES)
    # waut for one to end before starting the next
    yield env.process(bully.start_election())
    env.process(ring.start_election())

env.process(run_both_sim())

env.run()
