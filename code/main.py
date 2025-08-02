from node import Node, ringNode
from ring import ringSimulation
import simpy

# ------------ RING ALGORITHM SIMULATION ------------

# number of nodes in the system
N_NODES = 5

# create simpy environment
env = simpy.Environment()

# create nodes with IDs i = 1, 2, ...
nodes = []
for i in range(N_NODES):
    nodes.append(ringNode(env,i))

# pass the peers to the nodes
for i in range(N_NODES):
    nodes[i].obtain_peers(nodes)

# begin simulation
ring = ringSimulation(env, nodes, False)
env.process(ring.start_election())
env.run()

'''
# create nodes
nodes = []
for i in range(N_NODES):
    nodes.append(Node(i, nodes))

#   nodes[0].multicast("READY")         #   test multicast
nodes[0].send(1, "READY")
'''

