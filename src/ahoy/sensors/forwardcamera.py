from ahoy.sensor import Sensor
from ahoy.events.sensor import SensorEvent
from ahoy.util.geo import *

class ForwardCameraEvent(SensorEvent) :
    def __init__(self, owner_uid, poly, visible) :
        SensorEvent.__init__(self, owner_uid)
        self._poly = poly
        self._visible = visible

    def get_poly(self) :
        return self._poly

    def get_visible(self) :
        return self._visible

class ForwardCameraSensor(Sensor) :
    def __init__(self, bearing, fov, **kwds) :
        Sensor.__init__(self, **kwds)
        self._bearing = bearing
        self._fov = fov

    def run(self) :
        while True :
            lat, lon, agl = self.get_owner().get_position()
            cam_bearing = self.get_owner().get_bearing + self._bearing
            points = [self.get_position(), loc_from_bearing_dist(lat, lon, cam_bearing - self._fov / 2.0), loc_from_bearing_dist(lat, lon, cam_bearing + self._fov / 2.0)]
            visible = []
            for entity in self.get_owner().get_world().get_entities() :
                if entity.get_uid() != self.get_owner().get_uid() :
                    elat, elon, eagl = entity.get_location()
                    if point_in_poly(elat, elon, points) :
                        visible.append((e_lat, e_lon))

            self._publish_data(ForwardCameraEvent(self.get_owner().get_uid(), points, visible))
            time.sleep(0.01)
