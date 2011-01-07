from stage.event import Event

class CommunicationSendEvent(Event) :
    def __init__(self, message_inst, network) :
        self._message = message
        self._network = network

    def get_network(self) :
        return self._network

class CommunicationRecvEvent(Event) :
    def __init__(self, message_inst, network) :
        self._message = message_inst
        self._network = network_inst

    def get_network(self) :
        return self._network
