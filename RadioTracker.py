import json
from httplib import httplib

class constructor(object):
    
    json_data: dict = {}
    


class RadioTracker(object):
    
    
    def __init__(self, host = "meta.metacast.eu", type_of: str = "?radio=radioenergy") -> None:
        
        self.host = host
        self.type_of = type_of
        self.constructor = constructor()
    
    def __repr__(self):
        
        return f"<RadioTracker host={self.host}>"
    
    def capture(self):
        httplib_object: httplib.httplib = httplib.httplib(self.host, self.type_of, 80)
        response: str = httplib_object.create_request_get().work().payload.lstrip("\ufeff")
        self.constructor.json_data = json.loads(response.strip())
        
    def audio_sample(self, constructor,  type_of: str = "RADIO_ENERGY"):
        httplib_object: httplib.httplib = httplib.httplib(f"23543.live.streamtheworld.com", f"{type_of}AAC_L.aac", 443)
        received: bytes = httplib_object.create_request_file(constructor)
        return received
    
    def music_stream(self, constructor, writing_pipe, path, type_of: str = "RADIO_ENERGY"):
        httplib_object: httplib.httplib = httplib.httplib(f"23543.live.streamtheworld.com", f"{type_of}AAC_L.aac", 443)
        httplib_object.create_request_stream(constructor, writing_pipe, path)
        