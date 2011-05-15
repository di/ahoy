from ahoy.eventapi import EventAPI
from ahoy.events.startup import *

def stop() :
    _event_api = EventAPI()
    _event_api.publish(StopSimulationEvent())
    _event_api.stop()

stop()

