from ahoy.eventapi import EventAPI
from ahoy.events.communication import CommunicationSendEvent
from ahoy.events.communication import CommunicationSendEvent

class CommsEngine :
    def __init__(self) :
        self._event_api = EventAPI()
        self._event_api.start()
        self._simulation = None

        self._event_api.subscribe(CommunicationSendEvent, self._on_send)

    def get_node_from_agent(self, agent_uid) :
        return self._simulation.get_world().get_agent_mapping()[agent_uid]

    def set_simulation(self, simulation) :
        self._simulation = simulation

    def get_event_api(self) :
        return self._event_api

    def get_simulation(self) :
        return self._simulation

    def _on_send(self, event) :
        pass
