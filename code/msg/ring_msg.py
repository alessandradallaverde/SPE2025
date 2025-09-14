# this class represents a message passed during ring algorithm execution
#
# attributes
#   - type -> a string representing the type of the message (coordinator or election)
#   - transaction_id -> (unique) identifier of the messages exchanged during the same election 
#   - sender -> message's sender
class RingMsg:

    def __init__(self, type, transaction_id, sender):
        self.type = type
        self.transaction_id = transaction_id
        self.sender = sender

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, RingMsg):
            return self.type==__o.type and self.transaction_id==__o.transaction_id and self.sender==__o.sender
        return False

class ElectionRingMsg(RingMsg):

    # ids -> list of all nodes' ids collected so far 
    def __init__(self, transaction_id, sender, ids):
        super().__init__("ELECTION", transaction_id, sender)
        self.ids = ids

class CoordinatorRingMsg(RingMsg):

    # elected -> id of the new coordinator
    def __init__(self, transaction_id, sender, initiator, elected):
        super().__init__("COORDINATOR", transaction_id, sender)
        self.initiator = initiator
        self.elected = elected