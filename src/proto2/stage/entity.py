import sys
import pickle
from stage.eventapi import EventAPI

class Entity :
    def __init__(self, uid) :
        self._uid = uid
        self._event_api = None

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

    def run(self) :
        pass

if __name__ == '__main__' :
    inst = Entity.from_pickle(sys.argv[1])
    inst.run()
