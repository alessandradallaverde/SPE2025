# this class represents a message passed during ring algorithm execution
# attributes
#   type -> a string representing the type of the message (coordinator or election)
#   id   -> it is the id of the node the sender think is the coordinator
class RingMsg:

    def __init__(self, type, id):
        self.type = type
        self.id = id