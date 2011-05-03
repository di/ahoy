import time
from ahoy.eventapi import EventAPI
from ahoy.events.all import All

start = time.time()
def _on_event(event) :
    print time.time() - start, event.__class__.__name__
api = EventAPI()
api.subscribe(All, _on_event)
api.start()

while True :
    pass
