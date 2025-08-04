
# this class represents a message passed during bully algorithm execution
# attributes
#   type      -> a string representing the type of the message (coordinator, election or ok)
#   sender_id -> it is the id of the node that sent the message
class BullyMsg:
     
    def __init__(self, type, sender_id):
        self.type = type      
        self.sender_id = sender_id
    
    '''
    def copy(self):
        return Msg(self.type, self.sender_id)
    '''

# this class represents a message passed during ring algorithm execution
# attributes
#   type -> a string representing the type of the message (coordinator or election)
#   id   -> it is the id of the node the sender think is the coordinator
class RingMsg:

    def __init__(self, type, id):
        self.type = type
        self.id = id