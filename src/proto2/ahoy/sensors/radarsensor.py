import math
import time
from ahoy.sensor import Sensor
from ahoy.events.sensor import SensorEvent
from ahoy.util.geo import *

class RadarEvent(SensorEvent) :
    def __init__(self, owner_uid, bearing, distance, target_location) :
        SensorEvent.__init__(self, owner_uid)
        self._bearing = bearing
        self._distance = distance
        self._target_location = target_location

    def get_bearing(self) :
        return self._bearing

    def get_distance(self) :
        return self._distance

    def get_target_location(self) :
        return self._target_location

    def __str__(self) :
        if self._target_location != None :
            s = '%s %s %s %s %s' % (self.get_owner_uid(), math.degrees(self._bearing), self._distance, self._target_location[0], self._target_location[1])
        else :
            s = '%s %s none none none' % (self.get_owner_uid(), math.degrees(self._bearing))
        return s

class RadarSensor(Sensor) :
    def __init__(self, trans_power, trans_freq, gain, aperature, prop_fact, dwell_time, angle, **kwds) :
        Sensor.__init__(self, **kwds)
        self._trans_power = trans_power
        self._trans_freq = trans_freq
        self._gain = gain
        self._aperature = aperature
        self._prop_fact = prop_fact
        self._dwell_time = dwell_time
        self._angle = math.radians(angle)

    def run(self) :
        antenna_bearing = 0
        while True :
            angle_data = None
            for entity in self.get_world().get_entities() :
                if entity.get_uid() == self.get_owner().get_uid() :
                    continue
                lat, lon, agl = self.get_owner().get_position()
                e_lat, e_lon, e_agl = entity.get_position()

                lat = math.radians(lat)
                e_lat = math.radians(e_lat)
                lon = math.radians(lon)
                e_lon = math.radians(e_lon)
                
                y = math.sin(e_lon - lon) * math.cos(e_lat)
                x = math.cos(lat) * math.sin(e_lat) - math.sin(lat) * math.cos(e_lat) * math.cos(e_lon - lon)
                bearing = math.atan2(y, x) % (2*math.pi)
                
                if bearing >= antenna_bearing and bearing <= antenna_bearing + self._angle :
                    #dist = haver_distance(math.degrees(lat), math.degrees(lon), math.degrees(e_lat), math.degrees(e_lon))
                    dist = lin_distance(math.degrees(lat), math.degrees(lon), 0, math.degrees(e_lat), math.degrees(e_lon), 0)
                    est_dist = dist
                    if angle_data == None or angle_data[0] > est_dist :
                        x, y, z = sph_to_lin(lat, lon, agl)
                        e_vel_x, e_vel_y, e_vel_z = entity.get_lin_velocity()
                        e_x, e_y, e_z = sph_to_lin(e_vel_x, e_vel_y, e_vel_z)
                        angle = math.atan2(x - e_x, y - e_y)

                        proj_vel = entity.get_forward_velocity() * math.cos(angle)
                        freq_shift = 2 * proj_vel * self._trans_freq / 3e8

                        est_orth_vel = freq_shift * 3e8 / (2 * self._trans_freq)
                        angle_data = (est_dist, est_orth_vel, e_lat, e_lon)

            if angle_data != None :
                llat, llon, _ = self.get_owner().get_position()
                location = (math.degrees(angle_data[2]), math.degrees(angle_data[3]))
                #location = loc_from_bearing_dist(llat, llon, math.degrees(antenna_bearing), angle_data[0])
                #print 'bearing:', loc_from_bearing_dist(llat, llon, math.degrees(antenna_bearing), angle_data[0]), 'actual', location
                distance = angle_data[0]
                #print 'RADAR:', antenna_bearing, location
            else :
                location = None
                distance = None
            self._publish_data(RadarEvent(self.get_owner().get_uid(), antenna_bearing, distance, location))

            antenna_bearing = (antenna_bearing + self._angle) % (2 * math.pi)
            time.sleep(self._dwell_time)
