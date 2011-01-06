import sys
import time
from stage.eventapi import EventAPI
from stage.events.startup import StartupEvent, AckStartupEvent, StartSimulationEvent

class Simulation :
    def __init__(self, world_path) :
        self._event_api = EventAPI()
        self._startup_acks = set([])
        self._world = self._world_loader(world_path)

    def _world_loader(self, world_path) :
        world = __import__(world_path.split('.')[0])
        world = getattr(world, world_path.split('.')[1])
        return world

    def _on_ack_startup(self, event) :
        self._startup_acks.add(event.get_daemon_id())

    def start(self, wait) :
        self._event_api.subscribe(AckStartupEvent, self._on_ack_startup)
        self._event_api.publish(StartupEvent(self._world))
        
        time.sleep(wait)
        if len(self._startup_acks) > 0 :
            print 'Got %s startup acks.  Starting simulation.' % (len(self._startup_acks),)
            self._event_api.unsubscribe_all(AckStartupEvent)
            #TODO: Fix the division
            entities_per_phy_node = len(self._world.get_entities()) / float(len(self._startup_acks))
            mapping = {}
            for i, phy in enumerate(self._startup_acks) :
                alloc = mapping[i:i+2]
                if len(alloc) == 0 :
                    break
                mapping[phy] = alloc
            self._event_api.publish(StartSimulationEvent(mapping))
        else :
            print 'Got no startup acks.  Quitting...'

