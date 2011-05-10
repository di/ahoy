import sys
import time
import math
from threading import Thread, Condition
from ahoy.util.serialize import *
from ahoy.world import World
from ahoy.eventapi import EventAPI
from ahoy.events.move import EntityMoveEvent
from ahoy.util.geo import *
from ahoy.util.units import *

class Entity :
    MAX_DISTANCE = kilometers(0.001)
    def __init__(self, uid) :
        self._uid = uid
        self._lat = 0
        self._long = 0
        self._agl = 0
        self._params = {}
        self._event_api = None
        self._world = None
        self._velocity = (0, 0, 0)
        self._forward_velocity = 0
        self._bearing = 0
        self._turn_rate = 0

        self._sensors = {}

    def get_parameter(self, param, default=None) :
        if self._params.has_key(param) :
            return self._params[param]
        return default

    def set_parameter(self, param, value) :
        self._params[param] = value

    def add_sensor(self, name, sensor) :
        sensor.set_uid(len(self._sensors))
        self._sensors[name] = sensor
        sensor.set_owner(self)

    def get_sensor(self, name) :
        return self._sensors[name]

    def get_bearing(self) :
        return math.degrees(self._bearing)

    def get_lin_velocity(self) :
        return self._velocity

    def get_forward_velocity(self) :
        return self._forward_velocity

    def set_lin_velocity(self, v) :
        self._velocity = v

    def set_forward_velocity(self, v) :
        self._forward_velocity = v

    def set_world(self, world) :
        self._world = world

    def get_world(self) :
        return self._world

    def set_position(self, lat, long, agl) :
        self._lat = lat
        self._long = long
        self._agl = agl
        if self._event_api != None :
            self._event_api.publish(EntityMoveEvent(self, lat, long, agl, self._bearing, self._forward_velocity, self._velocity))

    def set_speed(self, vel, turn_rate) :
        self._forward_velocity = vel
        self._turn_rate = turn_rate

    def move(self, lat, lon, agl, forward_vel, vert_vel, block=False) :
        if self._move_thread != None :
            self._stop_move = True
            self._stopped_cond.acquire()
            self._stopped_cond.wait()
            self._stopped_cond.release()
            self._stop_move = False
        if not block :
            self._move_thread = Thread(target=self._iterate_move, args=(lat, lon, agl, forward_vel, vert_vel))
            self._move_thread.start()
        else :
            self._move_thread = self
            self._iterate_move(lat, lon, agl, forward_vel, vert_vel)
        
    def _iterate_move(self, lat, lon, agl, forward_vel, vert_vel) :
        last_tic = time.time() - Entity.MAX_DISTANCE / forward_vel
        self._forward_velocity = forward_vel
        while (lat != self._lat or lon != self._long or self._agl != agl) and not self._stop_move :
            lon1 = math.radians(self._long)
            lon2 = math.radians(lon)
            lat1 = math.radians(self._lat)
            lat2 = math.radians(lat)

            y = math.sin(lon2 - lon1) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
            self._bearing = math.atan2(y, x)

            self._velocity = (math.cos(self._bearing) * self._forward_velocity, math.sin(self._bearing) * self._forward_velocity, vert_vel)

            dt = time.time() - last_tic

            d = self._forward_velocity * dt
            R = kilometers(6378.1)
            new_lat = math.degrees(math.asin(math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(self._bearing)))
            new_lon = math.degrees(lon1 + math.atan2(math.sin(self._bearing)*math.sin(d/R)*math.cos(lat1), math.cos(d/R)-math.sin(lat1)*math.sin(new_lat)))
            if self._agl < agl :
                new_agl = min(self._agl + vert_vel * dt, agl)
            elif self._agl > agl :
                new_agl = max(0, self._agl - vert_vel * dt)
            else :
                new_agl = self._agl

            if haver_distance(self._lat, self._long, lat, lon) < d :
                self._velocity = (0, 0, 0)
                self._forward_velocity = 0
                self.set_position(lat, lon, agl)
                self._move_thread = None
                self._stopped_cond.acquire()
                self._stopped_cond.notify()
                self._stopped_cond.release()
                break

            self.set_position(new_lat, new_lon, new_agl)

            last_tic = time.time()
            time.sleep(Entity.MAX_DISTANCE / self._forward_velocity)

        self._move_thread = None
        self._stopped_cond.acquire()
        self._stopped_cond.notify()
        self._stopped_cond.release()

    def get_position(self) :
        return self._lat, self._long, self._agl

    def pickle(self) :
        return serialize(self)

    @staticmethod
    def from_pickle(pickled) :
        return unserialize(pickled)

    def get_event_api(self) :
        return self._event_api

    def get_uid(self) :
        return self._uid

    def initialize(self) :
        self._event_api = EventAPI()
        self._event_api.start()

        self._event_api.publish(EntityMoveEvent(self, self._lat, self._long, self._agl, self._forward_velocity, self._velocity))

        self._move_thread = None
        self._stop_move = False
        self._stopped_cond = Condition()

        for sensor in self._sensors.values() :
            Thread(target=sensor._run, args=(self.get_world(),)).start()

        Thread(target=self.move_loop).start()

    def run(self) :
        pass

    def move_loop(self) :
        last_tic = time.time()
        last_lat, last_long, last_bearing = self._lat, self._long, self._bearing

        while True :
            dt = time.time() - last_tic
            self._bearing += self._turn_rate * dt
            self._lat, self._long = loc_from_bearing_dist(self._lat, self._long, math.degrees(self._bearing), self._forward_velocity * dt)

            if last_lat != self._lat or last_long != self._long or last_bearing != self._bearing:
                if self._event_api != None :
                    self._event_api.publish(EntityMoveEvent(self, self._lat, self._long, self._agl, self._bearing, self._forward_velocity, self._velocity))
            last_lat, last_long, last_bearing = self._lat, self._long, self._bearing
            last_tic = time.time()
            time.sleep(0.1)

if __name__ == '__main__' :
    entity = Entity.from_pickle(sys.argv[1])

    world = World.from_pickle(sys.argv[2])
    world.initialize()

    entity.set_world(world)
    entity.initialize()
    entity.run()
