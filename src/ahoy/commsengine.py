from ahoy.eventapi import EventAPI
from ahoy.events.communication import CommunicationSendEvent

class CommsEngine :
    def __init__(self) :
        self._event_api = EventAPI()
        self._event_api.start()

        self._network_name = None
        self._world = None

        self._event_api.subscribe(CommunicationSendEvent, self._check_is_network)

    def get_world(self) :
        return self._world

    def set_world(self, world) :
        self._world = world

    def get_node_from_agent(self, agent_uid) :
        return self.get_world().get_agent_mapping()[agent_uid]

    def get_event_api(self) :
        return self._event_api

    def get_network_name(self) :
        return self._network_name

    def set_network_name(self, network_name) :
        self._network_name = network_name

    def _check_is_network(self, event) :
        if event.get_network() == self._network_name :
            self._on_send(event)

    def _on_send(self, event) :
        pass
