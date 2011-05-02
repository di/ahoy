import math
import time
from ahoy.sensor import Sensor
from ahoy.events.sensor import SensorEvent
from ahoy.util.geo import *

class CameraEvent(SensorEvent) :
    def __init__(self, owner_uid, sensor_id, visible, field) :
        SensorEvent.__init__(self, owner_uid)
        self._visible = visible
        self._field = field
        self._owner_uid = owner_uid
        self._sensor_uid = sensor_id
        #self._interval = interval

    # Returns a list of lat/lons for nodes visible w/in the field
    def get_visible(self) :
        return self._visible

    # Returns parameters for the field of vision in the form:
    # (max_lat, max_lon, min_lat, min_lon)
    def get_field(self) :
        return self._field

    def get_owner_uid(self) :
        return self._owner_uid

    def get_sensor_uid(self):
        return self._sensor_uid

    def __str__(self):
        out = ""
        for loc in self._visible:
            out += str(loc[0]) + "," + str(loc[1]) + ";"
        return out

class CameraSensor(Sensor) :
    def __init__(self, fov, interval) :
        Sensor.__init__(self)
        self._fov = fov
        self._interval = interval

    def run(self) :
        print "CAMERA IS RUNNING!"
        while True :
            visible = []

            lat, lon, agl = self.get_owner().get_position()
            app_size = agl / math.cos(self._fov / 2.0)
            min_lat = lat - app_size
            max_lat = lat + app_size
            min_lon = lon - app_size
            max_lon = lon + app_size

            for entity in self.get_world().get_entities() :
                if entity.get_uid() == self.get_owner().get_uid() :
                    continue
                e_lat, e_lon, e_agl = entity.get_position()
                if min_lat <= e_lat <= max_lat and min_lon <= e_lon <= max_lon :
                    visible.append((e_lat, e_lon, e_agl))
                    print "Spotted " + str(entity.get_uid()) + " at " + str(e_lat) + "," + str(e_lon)
                
            field = (max_lat, max_lon, min_lat, min_lon)
            self._publish_data(CameraEvent(self.get_owner().get_uid(), self.get_uid(), visible, field))
            time.sleep(self._interval)
