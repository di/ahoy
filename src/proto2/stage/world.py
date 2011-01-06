import pickle

class World :
    def __init__(self) :
        self._entities = set([])
        self._networks = set([])

    def add_entity(self, entity) :
        self._entities.add(entity)

    def get_entities(self) :
        return self._entities

    def get_networks(self) :
        return self._networks

    def pickle(self) :
        return pickle.dumps(self)

    @staticmethod
    def from_pickle(pickled) :
        return pickle.loads(pickled)
