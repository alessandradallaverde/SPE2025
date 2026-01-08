# this class represents a message passed during ring algorithm execution
#    attributes:
#        type - a string representing the type of the message (coordinator, election, ACK)
#        transaction_id - (unique) id of the messages coming from the same initiator election
#        sender - message sender
#        event - event for the ack 
class RingMsg():

    def __init__(self, type, transaction_id, sender, event = None):
        self.type = type
        self.transaction_id = transaction_id
        self.sender = sender
        self.ack_event =event

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, RingMsg):
            return self.type==__o.type and self.transaction_id==__o.transaction_id and self.sender==__o.sender
        return False
    
    # method to give to the message an ack event to be triggered
    #    params:
    #       event - event reference
    def set_event(self, event):
        self.ack_event = event

# this class represents an ELECTION message (without ack)
#    attributes:
#        ids - list of all nodes ids collected so far 
class ElectionRingMsg(RingMsg):

    def __init__(self, transaction_id, sender, ids):
        super().__init__("ELECTION", transaction_id, sender)
        self.ids = ids

# this class represents a COORDINATOR message (without ack)
#    attributes:
#        elected - id of the new coordinator
#        initiator - id of the initiator of the messages cycle
class CoordinatorRingMsg(RingMsg):

    def __init__(self, transaction_id, sender, initiator, elected):
        super().__init__("COORDINATOR", transaction_id, sender)
        self.initiator = initiator
        self.elected = elected