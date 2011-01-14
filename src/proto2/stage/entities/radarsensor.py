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

    def _get_power(self, distance, src_power) :
        d0 = 1.0 / 1000.0  # 1 meter
        ref_loss = 46.6777 # loss @ 1 meter
        l = 3.0 # path loss exponent
        flat_fade_factor = 0
        tx_power_dbm = 10 * math.log(src_power, 10)
        if distance <= d0 :
            return tx_power_dbm - ref_loss
        loss = -ref_loss - 10 * l * math.log(distance / d0, 10) + flat_fade_factor
        return tx_power_dbm + loss

    def run(self) :
        while True :
            lat, lon, agl = self.get_position()
            self._state = {}
            for entity in self.get_world().get_entities() :
                if entity.get_uid() == self.get_uid() :
                    continue
                e_lat, e_lon, e_agl = entity.get_position()

                dist = lin_distance(e_lat, e_lon, e_agl, lat, lon, agl)
                # Outbound pathloss
                #outbound_pwr = self._get_power(dist, self._trans_power)
                outbound_pwr = self._trans_power
                # Received power calculation
                recv_pwr = outbound_pwr * self._gain * self._aperature * entity.get_rcs() * math.pow(self._prop_fact, 4) 
                recv_pwr /= pow(4 * math.pi, 2) * lin_distance(lat, lon, agl, e_lat, e_lon, e_agl)
                # Inbound pathloss
                #recv_pwr = self._get_power(dist, recv_pwr)

                # Calculates Doppler shift and determines frequency shift
                # TODO: Currently ignores altitude/vertical velocity
                x, y, z = sph_to_lin(lat, lon, agl)
                e_vel_x, e_vel_y, e_vel_z = entity.get_lin_velocity()
                e_x, e_y, e_z = sph_to_lin(e_vel_x, e_vel_y, e_vel_z)
                angle = math.atan2(x - e_x, y - e_y)

                proj_vel = entity.get_forward_velocity() * math.cos(angle)
                freq_shift = 2 * proj_vel * self._trans_freq / 3e8

                # Estimates the (orthogonal) velocity of the entity
                est_orth_vel = freq_shift * 3e8 / (2 * self._trans_freq)

                self._state[(e_lat, e_lon, e_agl)] = (recv_pwr, freq_shift, est_orth_vel)
                for e in self._state.keys() :
                    print e, self._state[e]

                time.sleep(self._interval)
