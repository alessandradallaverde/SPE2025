from node import Node

N_NODES = 10

# create nodes
nodes = []
for i in range(N_NODES):
    nodes.append(Node(i, nodes))

#   nodes[0].multicast("READY")         #   test multicast
nodes[0].send(1, "READY")

