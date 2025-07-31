class Msg:
     
    def __init__(self, type, sender_id):
        self.type = type      
        self.sender_id = sender_id                                    
        #   other parameters ...   
    
    def copy(self):
        return Msg(self.type, self.sender_id)
