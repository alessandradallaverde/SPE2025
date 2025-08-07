from node.node import Node
from msg.bully_msg import BullyMsg

# this class represents a node in the bully algorithm execution
class BullyNode(Node):

    def __init__(self, env, id):
       super().__init__(env, id)
       self.elected = -1
       self.is_waiting = False
       self.blocked = False

    def send(self, type, dest_id):
        if not self.peers[dest_id].crashed:
            # create the election message 
            election_msg = BullyMsg(type, self.id)

            # DEBUG
            print(f"Node {self.id} sends {type} to node {dest_id}")
            
            yield self.env.timeout(20)
            # send the message 
            yield self.peers[dest_id].queue.put(election_msg) 
            self.env.process(self.peers[dest_id].receive())


    def receive(self):
        msg = yield self.queue.get()
        if msg.type == "ELECTION":
            if msg.sender_id == -1:
                # start election
                print(f"Node {self.id} detected coordinator crash")
            else:    
                # DEBUG
                print(f"Node {self.id} receives ELECTION message from node {msg.sender_id}")

            if self.id > msg.sender_id:
                if msg.sender_id != -1:
                    # if id is greater than sender: stop election
                    self.env.process(self.send("OK", msg.sender_id))
                if not self.is_waiting:
                    # only start election ONCE
                    self.is_waiting = True
                    # send ELECTION messages to all nodes with greater id
                    for i in range(self.id + 1, len(self.peers)):
                        self.env.process(self.send("ELECTION", i))
                    # TO BE CHANGED: works in synchronous systems where you have an upper bound of network delays
                    yield self.env.timeout(40 * len(self.peers) + 1)
                    self.is_waiting = False
                    #   wait for a certain time to be passed ... if it wasn't stopped it is elected
                    if not self.blocked:
                        for i in range(len(self.peers)):
                            self.env.process(self.send("COORDINATOR", self.peers[i].id))

        elif msg.type == "OK":
            # DEBUG
            print(f"Node {self.id} receives OK message from node {msg.sender_id}")
            # stop election
            self.blocked = True

        elif msg.type == "COORDINATOR":
            # DEBUG
            print(f"Node {self.id} elects {msg.sender_id} as coordinator")
            self.elected = msg.sender_id
            # if election terminated trigger finish event
            if self.finished():
                self.finish.succeed()

    # returns True if all nodes decided on coordinator
    def finished(self):
        for i in range(len(self.peers)):
            if self.peers[i].elected == -1 and not self.peers[i].crashed:     # count only non crashed processes
                return False
        return True      

    def reset(self):
        self.blocked = False
        self.crashed = False
        self.elected = -1
        self.is_waiting = False      
