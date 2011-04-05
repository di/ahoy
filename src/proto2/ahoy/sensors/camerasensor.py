import time
from ahoy.sensor import Sensor
from ahoy.events.sensor import SensorEvent
from ahoy.util.geo import *

class CameraEvent(SensorEvent) :
    def __init__(self, owner_uid, visible, interval) :
        SensorEvent.__init__(self, owner_uid)
        self._visible = visible
        self._interval = interval

    def get_visible(self) :
        return self._visible

class CameraSensor(Sensor) :
    def __init__(self, bearing, fov) :
        Sensor.__init__(self)
        self._bearing = bearing
        self._fov = fov

    def run(self) :
        while True :
            visible = []
            lat, lon, agl = self.get_owner().get_position()
            for entity in self.get_world().get_entities() :
                if entity.get_uid() == self.get_owner().get_uid() :
                    continue
                e_lat, e_lon, e_agl = entity.get_position()
                bearing = bearing_from_pts(lat, long, e_lat, e_lon)
                diff = (bearing - self._bearing) % 360
                diff = min(diff, abs(diff - 360))
                if diff <= self._fov :
                    visible.append(bearing)

            self._publish_data(CameraEvent(self.get_owner().get_uid(), visible))
            time.sleep(self._interval)
