from ahoy.event import Event

class CommunicationSendEvent(Event) :
    def __init__(self, src_agent_uid, src_iface_name, message_inst, network) :
        Event.__init__(self)
        self._src_agent_uid = src_agent_uid
        self._src_iface_name = src_iface_name
        self._message = message_inst
        self._network = network

    def get_src_agent_uid(self) :
        return self._src_agent_uid

    def get_src_iface_name(self) :
        return self._src_iface_name

    def get_message(self) :
        return self._message

    def get_network(self) :
        return self._network

class CommunicationRecvEvent(Event) :
    def __init__(self, src_agent_uid, src_iface_name, message_inst, network) :
        Event.__init__(self)
        self._src_agent_uid = src_agent_uid
        self._src_iface_name = src_iface_name
        self._message = message_inst
        self._network = network

    def get_src_agent_uid(self) :
        return self._src_agent_uid

    def get_src_iface_name(self) :
        return self._src_iface_name

    def get_message(self) :
        return self._message

    def get_network(self) :
        return self._network
