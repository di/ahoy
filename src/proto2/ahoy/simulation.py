import sys
import time
from ahoy.eventapi import EventAPI
from ahoy.world import World
from ahoy.events.startup import *

class Simulation :
    def __init__(self, world_inst) :
        self._event_api = EventAPI()
        self._event_api.start()
        self._startup_acks = set([])
        self._world = world_inst

    def get_world(self) :
        return self._world

    def _on_ack_startup(self, event) :
        print 'Got ack startup:', event.get_daemon_id()
        self._startup_acks.add(event.get_daemon_id())

    def start(self, wait) :
        self._event_api.subscribe(AckStartupEvent, self._on_ack_startup)
        # Do *NOT* change self._world after this point.  It is pickled here and sent to other phy nodes
        self._event_api.publish(StartupEvent(self._world))
        
        time.sleep(wait)
        if len(self._startup_acks) > 0 :
            print 'Got %s startup acks.  Starting simulation.' % (len(self._startup_acks),)
            self._event_api.unsubscribe_all(AckStartupEvent)

            #TODO: Fix the division
            entities_per_phy_node = int(len(self._world.get_entities()) / float(len(self._startup_acks)))
            print '    allocating %s entities per node' % entities_per_phy_node
            mapping = {}
            to_allocate = list(self._world.get_entities())
            for i, phy in enumerate(list(self._startup_acks)) :
                alloc = to_allocate[i*entities_per_phy_node:(i+1)*entities_per_phy_node]
                print i, alloc
                if len(alloc) == 0 :
                    break
                mapping[phy] = alloc

            self._world.initialize()
            self._event_api.publish(StartSimulationEvent(mapping))
        else :
            print 'Got no startup acks.  Quitting...'

    def stop(self) :
        self._event_api.publish(StopSimulationEvent())
        self._event_api.stop()
