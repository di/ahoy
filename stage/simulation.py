import sys
import time
from stage.eventapi import EventAPI
from stage.events.startup import StartupEvent, AckStartupEvent, StartSimulationEvent

class Simulation :
    def __init__(self) :
        self._event_api = EventAPI()
        self._startup_acks = set([])

    def _on_ack_startup(self, event) :
        self._startup_acks.add(event.get_daemon_id())

    def start(self, world, wait) :
        self._event_api.subscribe(AckStartupEvent, self._on_ack_startup)
        self._event_api.publish(StartupEvent(world))
        
        time.sleep(wait)
        if len(self._startup_acks) > 0 :
            print 'Got %s startup acks.  Starting simulation.' % (len(self._startup_acks),)
            self._event_api.unsubscribe_all(AckStartupEvent)
            self._event_api.publish(StartSimulationEvent())
        else :
            print 'Got no startup acks.  Quitting...'

def world_loader(world_path) :
    world = __import__(world_path.split('.')[0])
    world = getattr(world, world_path.split('.')[1])
    return world

if __name__ == '__main__' :
    if len(sys.argv) < 2 :
        print ' usage: python simulation.py <worldfile.worldclass>'
        sys.exit(0)
    Simulation().start(world_loader(sys.argv[1]), 2)
