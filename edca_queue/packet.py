class packet(object):
    def __init__(self, payload):
        self._deadline = 0.100
        self._payload = payload
        
        
    def get_deadline(self):
        return self._deadline
    
    def set_deadline(self, deadline):
        self._deadline = deadline
    
    def get_payload(self):
        return self._payload
    
    