import json

class Match():
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def __init__(self, match_id, match_detail, match_timeline):
        self.id = match_id
        self.detail = match_detail
        self.timeline = match_timeline