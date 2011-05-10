import math
import time
from ahoy.sensor import Sensor
from ahoy.events.sensor import SensorEvent
from ahoy.events.chemical import ChemicalSpillEvent
from ahoy.eventapi import EventAPI
from ahoy.util.geo import *

class ChemicalDetectEvent(SensorEvent) :
    def __init__(self, owner_uid, location) :
        SensorEvent.__init__(self, owner_uid)
        self._location = location

    def get_location(self):
        return self._location

class ChemicalSensor(Sensor) :
    def __init__(self, interval) :
        Sensor.__init__(self)
        self._interval = interval
        self._spill_occurred = False
        self._spill_event = None
        self._event_api = None

##    def initialize(self):
##        self._event_api = EventAPI()
##        self._event_api.start()
##        self._event_api.subscribe(ChemicalSpillEvent, self._on_spill)

    def run(self) :

        self._event_api = EventAPI()
        self._event_api.start()
        self._event_api.subscribe(ChemicalSpillEvent, self._on_spill)

        while True :

            # If sensors aren't listening/publishing directly to API,
            # how is ChemicalSensor to know that a chemical spill has occurred?
            # for now, just assuming owner will tell chemical sensor this info through _on_spill() below

            if self._spill_occurred:

                lat, lon, agl = self.get_owner().get_position()

                # spill location
                spill_lat, spill_lon, spill_agl = self._spill_event.get_location()

                # if spill location is by latitude above the spill, just ignore the spill.
                # This is for AHOY team's demo purposes only, as spill will only travel south.
                if spill_lat < lat:
                    self._spill_occurred = False
                    self._spill_event = None
                else:
                    distance = haver_distance( lat, lon, spill_lat, spill_lon )
                    # for now, assuming spill spreads at a constant rate (does not slow down)
                    time_to_reach_sensor = distance / self._spill_event.get_intensity()
                    time_to_reach_sensor *= self._interval
                    print 'Sensor at ', self.get_owner().get_uid(), ' will go off at ', time_to_reach_sensor

                    # wait until chemical spill would have reached self, then publish ChemicalDetectEvent
                    time.sleep(time_to_reach_sensor)
                    self._publish_data( ChemicalDetectEvent(self.get_owner().get_uid(), self.get_owner().get_position() ) )

                    # clear spill event data
                    self._spill_occurred = False
                    self._spill_event = None

            time.sleep( self._interval )


    def _on_spill( self, event ):
        self._spill_occurred = True
        self._spill_event = event
