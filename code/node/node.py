from simpy import Store

class Node:

    def __init__(self, env, id):
        self.id = id                                       
        self.queue = Store(env)
        self.crashed = False
        self.env = env
        self.elected = -1

    def obtain_peers(self, peers):
        self.peers = peers

    def crash(self):
        self.crashed = True

        # DEBUG
        print(f"Time {self.env.now:.2f}: Node {self.id} crashes")