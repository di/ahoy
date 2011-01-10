import pickle
from stage.eventapi import EventAPI
from stage.events.move import EntityMoveEvent

class World :
    def __init__(self) :
        self._entities = {}
        self._networks = {}
        self._event_api = None

    def add_entity(self, entity) :
        self._entities[entity.get_uid()] = entity

    def get_entities(self) :
        return self._entities.values()

    def get_entity(self, uid) :
        return self._entities[uid]

    def add_network(self, network) :
        self._networks[network.get_name()] = network

    def get_networks(self) :
        return self._networks.values()

    def get_network(self, name) :
        return self._networks[name]

    def initialize(self) :
        self._event_api = EventAPI()
        self._event_api.start()
        self._event_api.subscribe(EntityMoveEvent, self._on_entity_move)

    def _on_entity_move(self, event) :
        self.get_entity(event.get_uid()).set_position(event.get_lat(), event.get_long(), event.get_agl())

    def pickle(self) :
        return pickle.dumps(self)

    @staticmethod
    def from_pickle(pickled) :
        return pickle.loads(pickled)
