from msg import Msg

class Node:

    def __init__(self, id, peers):
        self.id = id
        self.peers = peers                                          #   list of other nodes
        self.free = True
        self.queue = []
        self.crashed = False
    
    def process_msg(self, msg):
        self.queue.append(msg)

        if self.free:
            if self.queue.__len__() != 0:
                self.free = False
                msg = self.queue.pop(0)

                self.log_msg(msg)       
                #   type to test message sending functionality         
                if msg.type == "READY":
                    self.send( msg.sender_id, "ACK" )

                self.free = True
    

    def send(self, dest_id, msg_type):
        #   network delays?
        self.peers[dest_id].receive(Msg(msg_type, self.id))
    
    def multicast(self, msg_type):
        #   for better network delays reorder nodes before multicast
        for i in range(self.peers.__len__()):
            if self.id != i:
                self.send(i, msg_type)

    def receive(self, msg):
        if not self.crashed:
            self.process_msg(msg)
    
    def crash(self):
        self.crashed = True
    
    def start_bully_election(self):
        print("Start Bully election algorithm")
    
    def start_ring_election(self):
        print("Start Ring election algorithm")

    def log_msg(self, msg):        
        print( self.to_string() + ": " + self.peers[msg.sender_id].to_string() + " sent \"" + msg.type + "\"" )
    
    def to_string(self):
        return "Node " + str(self.id)

    
    