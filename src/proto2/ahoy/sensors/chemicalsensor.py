import math
import time
from ahoy.sensor import Sensor
from ahoy.events.sensor import SensorEvent
from ahoy.event import Event
from ahoy.util.geo import *

class ChemicalSpillEvent(Event) :
    def __init__(self, owner_uid, location, intensity) :
        SensorEvent.__init__(self, owner_uid)
        self._location = location
        self._intensity = intensity

    def get_location(self):
        return self._location

    def get_intensity(self):
        return self._intensity

class ChemicalDetectEvent(SensorEvent) :
    def __init__(self, owner_uid, location) :
        SensorEvent.__init__(self, owner_uid)
        self._location = location

    def get_location(self):
        return self._location

class ChemicalSensor(Sensor) :
    def __init__(self, loc, interval) :
        Sensor.__init__(self)
        self._loc = loc
        self._interval = interval
        self._spill_occurred = False
        self._spill_event = None

    def run(self) :
        while True :

            # If sensors aren't listening/publishing directly to API,
            # how is ChemicalSensor to know that a chemical spill has occurred?
            # for now, just assuming owner will tell chemical sensor this info through _on_spill() below

            if self._spill_occurred:

                lat, lon, agl = self.get_owner().get_position()

                spill_lat, spill_lon = self._spill_event.get_location()
                distance = haver_distance( lat, lon, spill_lat, spill_lon )
                # for now, assuming spill spreads at a constant rate (does not slow down)
                time_to_reach_sensor = distance / self._spill_event.get_intensity()

                time.sleep(time_to_reach_sensor)
                self._publish_data( ChemicalDetectEvent(self.get_owner().get_uid(), self._loc) )
                # clear spill event data
                self._spill_occurred = False
                self._spill_event = None


            time.sleep( self._interval )


    def _on_spill( self, event ):
        self._spill_occurred = True
        self._spill_event = event
