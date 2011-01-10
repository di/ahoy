import sys
import time
from stage.eventapi import EventAPI
from stage.world import World
from stage.events.startup import StartupEvent, AckStartupEvent, StartSimulationEvent
from stage.mcpush import McPush

class Simulation :
    def __init__(self, world_inst, comms_module, forward_port=None) :
        self._event_api = EventAPI()
        self._event_api.start()
        self._startup_acks = set([])
        self._comms_module = comms_module
        self._comms_module.set_simulation(self)
        self._world = world_inst
        self._forward_port = forward_port

    def get_world(self) :
        return self._world

    def _on_ack_startup(self, event) :
        self._startup_acks.add(event.get_daemon_id())

    def start(self, wait) :
        self._event_api.subscribe(AckStartupEvent, self._on_ack_startup)
        # Do *NOT* change self._world after this point.  It is pickled here and sent to other phy nodes
        self._event_api.publish(StartupEvent(self._world))
        
        time.sleep(wait)
        if len(self._startup_acks) > 0 :
            print 'Got %s startup acks.  Starting simulation.' % (len(self._startup_acks),)
            self._event_api.unsubscribe_all(AckStartupEvent)

            if self._forward_port != None :
                print 'Starting push on port %s' % self._forward_port
                McPush(self._forward_port)
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