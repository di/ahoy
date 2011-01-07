import sys
import pickle
from stage.eventapi import EventAPI

class Entity :
    def __init__(self, uid) :
        self._uid = uid
        self._lat = 0
        self._long = 0
        self._agl = 0

    def set_position(self, lat, long, agl) :
        self._lat = lat
        self._long = long
        self._agl = agl

    def get_position(self) :
        return self._lat, self._long, self._agl

    def pickle(self) :
        return pickle.dumps(self)

    @staticmethod
    def from_pickle(pickled) :
        return pickle.loads(pickled)

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
    inst = Entity.from_pickle(sys.argv[1])
    inst.initialize()
    inst.run()
