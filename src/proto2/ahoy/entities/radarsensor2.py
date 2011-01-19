import math
import time
from ahoy.entity import Entity
from ahoy.events.sensor import RadarEvent
from ahoy.util.geo import *

class RadarSensor2(Entity) :
    def __init__(self, uid, trans_power, trans_freq, gain, aperature, prop_fact, dwell_time, angle) :
        Entity.__init__(self, uid)
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
                if entity.get_uid() == self.get_uid() :
                    continue
                lat, lon, agl = self.get_position()
                e_lat, e_lon, e_agl = entity.get_position()

                lat = math.radians(lat)
                e_lat = math.radians(e_lat)
                lon = math.radians(lon)
                e_lon = math.radians(e_lon)
                
                y = math.sin(e_lon - lon) * math.cos(e_lat)
                x = math.cos(lat) * math.sin(e_lat) - math.sin(lat) * math.cos(e_lat) * math.cos(e_lon - lon)
                bearing = math.atan2(y, x) % (2*math.pi)
                
                if bearing >= antenna_bearing and bearing <= antenna_bearing + self._angle :
                    dist = haver_distance(e_lat, e_lon, lat, lon)
                    dt = 2*dist / 3e8
                    est_dist = dt * 3e8 / 2.0
                    if angle_data == None or angle_data > est_dist :
                        x, y, z = sph_to_lin(lat, lon, agl)
                        e_vel_x, e_vel_y, e_vel_z = entity.get_lin_velocity()
                        e_x, e_y, e_z = sph_to_lin(e_vel_x, e_vel_y, e_vel_z)
                        angle = math.atan2(x - e_x, y - e_y)

                        proj_vel = entity.get_forward_velocity() * math.cos(angle)
                        freq_shift = 2 * proj_vel * self._trans_freq / 3e8

                        # Estimates the (orthogonal) velocity of the entity
                        est_orth_vel = freq_shift * 3e8 / (2 * self._trans_freq)
                        angle_data = (est_dist, est_orth_vel)

            self.get_event_api().publish(RadarEvent(self.get_uid(), (antenna_bearing, angle_data)))

            antenna_bearing = (antenna_bearing + self._angle) % (2 * math.pi)
            time.sleep(self._dwell_time)
