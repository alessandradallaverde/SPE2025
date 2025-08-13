# this class represents a message passed during ring algorithm execution
# attributes
#   type -> a string representing the type of the message (coordinator or election)
class RingMsg:

    def __init__(self, type):
        self.type = type

class ElectionRingMsg(RingMsg):
    def __init__(self, ids):
        super().__init__("ELECTION")
        self.ids = ids

class CoordinatorRingMsg(RingMsg):
    def __init__(self, initiator, elected):
        super().__init__("COORDINATOR")
        self.initiator = initiator
        self.elected = elected
