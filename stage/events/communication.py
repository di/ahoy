from stage.event import Event

class CommunicationSendEvent(Event) :
    def __init__(self, src, message_inst, network) :
        Event.__init__(self)
        self._src = src
        self._message = message_inst
        self._network = network

    def get_src(self) :
        return self._src

    def get_message(self) :
        return self._message

    def get_network(self) :
        return self._network

class CommunicationRecvEvent(Event) :
    def __init__(self, src, message_inst, network) :
        Event.__init__(self)
        self._src = src
        self._message = message_inst
        self._network = network

    def get_src(self) :
        return self._src

    def get_message(self) :
        return self._message

    def get_network(self) :
        return self._network
