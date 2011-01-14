import time
import math
from stage.entity import Entity
from stage.util.geo import *

class RadarSensor(Entity) :
    def __init__(self, uid, trans_power, trans_freq, gain, aperature, prop_fact, interval) :
       Entity.__init__(self, uid) 
       self._trans_power = trans_power
       self._trans_freq = trans_freq
       self._gain = gain
       self._aperature = aperature
       self._prop_fact = prop_fact
       self._interval = interval
       self._state = {}

    def get_state(self) :
        return self._state.copy()

    def run(self) :
        lat, lon, agl = self.get_position()
        while True :
            self._state = {}
            for entity in self.get_world().get_entities() :
                if entity.get_uid() == self.get_uid() :
                    continue
                e_lat, e_lon, e_agl = entity.get_position()

                recv_pwr = self._trans_power * self._gain * self._aperature * entity.get_rcs() * math.pow(self._prop_fact, 4) 
                recv_pwr /= pow(4 * math.pi, 2) * lin_distance(lat, lon, agl, e_lat, e_lon, e_agl)

                # TODO: Currently ignores altitude/vertical velocity
                x, y, z = sph_to_lin(lat, lon, agl)
                e_vel_x, e_vel_y, e_vel_z = entity.get_lin_velocity()
                print 'LIN VEL', entity.get_uid(), ':', e_vel_x, e_vel_y, e_vel_z
                e_x, e_y, e_z = sph_to_lin(e_vel_x, e_vel_y, e_vel_z)
                angle = math.atan2(x - e_x, y - e_y)

                proj_vel = entity.get_forward_velocity() * math.cos(angle)
                freq_shift = 2 * proj_vel * self._trans_freq / 3e8

                self._state[(e_lat, e_lon, e_agl)] = (recv_pwr, freq_shift)
                for e in self._state.keys() :
                    print e, self._state[e]

                time.sleep(self._interval)
