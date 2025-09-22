from simpy import Store

# this class represents a node in the network 
#  
#   attributes:
#       - id -> (unique) identifier of the node
#       - queue -> messages' queue
#       - crashed -> boolean value, if true the node is crashed
#       - env -> simpy environment
#       - elected -> id of the new coordinator
class Node:

    def __init__(self, env, id):
        self.id = id                                       
        self.queue = Store(env)
        self.crashed = False
        self.env = env
        self.elected = -1

    # method to se the peers
    def obtain_peers(self, peers):
        self.peers = peers

    # method to crash the node
    def crash(self):
        self.crashed = True
        '''
        # DEBUG
        print(f"Time {self.env.now:.2f}: Node {self.id} crashes")
        '''