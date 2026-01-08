from simpy import Store

# this class represents a node in the network 
#   attributes:
#       id - (unique) identifier of the node
#       queue - messages queue
#       crashed - boolean value, if true the node is crashed
#       env - simpy environment
#       elected - id of the new coordinator
#       delay_mean - exponential mean for delays
class Node:

    def __init__(self, env, id, delay_mean):
        self.id = id                                       
        self.queue = Store(env)
        self.crashed = False
        self.env = env
        self.elected = -1
        self.delay_mean = delay_mean

    # method to set the peers
    #   params:
    #       peers - node peers
    def obtain_peers(self, peers):
        self.peers = peers

    # method to make the node crash
    def crash(self):
        self.crashed = True