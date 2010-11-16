from stage.event import Event

class NetworkSim :
    def __init__(self, simulation) :
        self._simulation = simulation

    def on_sent_event(self, event) :
        self._simulation.get_api().get_event_channel().publish(Event('RECV', event.get_model()))
