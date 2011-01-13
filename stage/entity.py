import sys
import time
import math
from threading import Thread
from stage.util.serialize import *
from stage.world import World
from stage.eventapi import EventAPI
from stage.events.move import EntityMoveEvent
from stage.util.geo import *

class Entity :
    TIC_INTERVAL = .5 # seconds
    def __init__(self, uid) :
        self._uid = uid
        self._lat = 0
        self._long = 0
        self._agl = 0
        self._event_api = None
        self._world = None

    def set_world(self, world) :
        self._world = world

    def get_world(self) :
        return self._world

    def set_position(self, lat, long, agl) :
        self._lat = lat
        self._long = long
        self._agl = agl
        if self._event_api != None :
            self._event_api.publish(EntityMoveEvent(self._uid, lat, long, agl))

    def move(self, lat, lon, agl, forward_vel, vert_vel) :
        Thread(target=self._move_tic, args=(lat, lon, agl, forward_vel, vert_vel)).start()
        
    def _move_tic(self, lat, lon, agl, forward_vel, vert_vel) :
        last_tic = time.time() - Entity.TIC_INTERVAL
        while lat != self._lat or lon != self._long or self._agl != agl :
            lon1 = math.radians(self._long)
            lon2 = math.radians(lon)
            lat1 = math.radians(self._lat)
            lat2 = math.radians(lat)

            y = math.sin(lon2 - lon1) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
            bearing = math.degrees(math.atan2(y, x))
            bearing = (bearing + 360) % 360

            dt = time.time() - last_tic
            # may break on 0?
            dlat, dlon = linear_to_degree(self._lat, self._long, math.sin(math.radians(bearing)) * forward_vel * dt, math.cos(math.radians(bearing)) * forward_vel * dt)
            dagl = (agl - self._agl) * vert_vel * dt
            print bearing, dlat, dlon, self._lat - dlat, self._long - dlon, self._agl + dagl

            self.set_position(self._lat - dlat, self._long - dlon, self._agl + dagl)

            last_tic = time.time()
            time.sleep(Entity.TIC_INTERVAL)

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

    def run(self) :
        pass

if __name__ == '__main__' :
    entity = Entity.from_pickle(sys.argv[1])

    world = World.from_pickle(sys.argv[2])
    world.initialize()

    entity.set_world(world)
    entity.initialize()
    entity.run()
