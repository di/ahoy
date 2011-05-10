import random
import time
from ahoy.agent import Agent
from ahoy.eventapi import EventAPI
from ahoy.events.chemical import ChemicalSpillEvent

# Publishes a single chemical spill event at a given time
class ChemicalSpillAnnounceAgent(Agent) :
    def __init__(self, owner_node, interval, announce_time, rate) :
        Agent.__init__(self, owner_node)
        self._interval = interval
        self._announce_time = announce_time
        self._announce_rate = rate
        self._total_time = 0
        self._announced_spill = False
        self._event_api = None
        print 'created ChemicalSpillAnnounceAgent'

##    def initialize(self):
##        print 'Initializing ChemicalSpillAnnounceAgent'
##        self._event_api = EventAPI()
##        self._event_api.start()

    def run(self) :
        ##o_lat, o_lon, o_agl = self.get_owner_node().get_position()

        self._event_api = EventAPI()
        self._event_api.start()

        while not self._announced_spill:
            if self._total_time > self._announce_time:
                # pass owner_uid, location, rate=5
                print 'Agent about to publish ChemicalSpillEvent....'
                self._event_api.publish( ChemicalSpillEvent(self.get_owner_node().get_position(), self._announce_rate))
                self._announced_spill = True
            else:
                print 'the time has not yet come!'
            time.sleep( self._interval )
            self._total_time += self._interval
