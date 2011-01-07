import pickle

class World :
    def __init__(self) :
        self._entities = {}
        self._networks = {}

    def add_entity(self, entity) :
        self._entities[entity.get_uid()] = entity

    def get_entities(self) :
        return self._entities.values()

    def get_entity(self, uid) :
        return self._entities[uid]

    def get_networks(self) :
        return self._networks.values()

    def get_network(self, name) :
        return self._networks[name]

    def pickle(self) :
        return pickle.dumps(self)

    @staticmethod
    def from_pickle(pickled) :
        return pickle.loads(pickled)
