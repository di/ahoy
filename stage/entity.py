import sys
from stage.util.serialize import *
from stage.world import World
from stage.eventapi import EventAPI
from stage.events.move import EntityMoveEvent

class Entity :
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
