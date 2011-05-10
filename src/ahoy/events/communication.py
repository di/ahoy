from ahoy.event import Event

class CommunicationSendEvent(Event) :
    def __init__(self, src_agent_uid, message_inst, network) :
        Event.__init__(self)
        self._src_agent_uid = src_agent_uid
        self._message = message_inst
        self._network = network

    def get_src_agent_uid(self) :
        return self._src_agent_uid

    def get_message(self) :
        return self._message

    def get_network(self) :
        return self._network

class CommunicationRecvEvent(Event) :
    def __init__(self, src_agent_uid, recvrs, message_inst, network) :
        Event.__init__(self)
        self._src_agent_uid = src_agent_uid
        self._recvrs = recvrs
        self._message = message_inst
        self._network = network

    def get_src_agent_uid(self) :
        return self._src_agent_uid

    def get_recvrs(self) :
        return self._recvrs

    def get_message(self) :
        return self._message

    def get_network(self) :
        return self._network
