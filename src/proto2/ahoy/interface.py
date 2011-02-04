from ahoy.events.communication import CommunicationRecvEvent, CommunicationSendEvent

class Interface :
    def __init__(self, name, network, **kwds) :
        self._name = name
        self._owner = None
        self._recv_callback = None
        self._network_name = network.get_name()
        self._attrs = kwds
        network.add_interface(self)

    def _on_communication(self, event) :
        # Connected to same network & this node received the message? (not necessarily a destination)
        if event.get_network() == self._network_name and self._owner.get_uid() in event.get_recvrs() :
            # Is the message bound for a local agent?
            if event.get_message().get_dest_agent() == '*' or event.get_message().get_dest_agent() in self.get_owner().get_agent_uids() :
                if self._recv_callback != None :
                    if self._owner.get_routing_agent() is not None :
                        self._owner.get_routing_agent().handle_delivery(event, self)
                    self._recv_callback(event, iface=self)
            else :
                if self._owner.get_routing_agent() is not None :
                    self._owner.get_routing_agent().handle_forward(event, self)

    def connect(self) :
        self._owner.get_event_api().subscribe(CommunicationRecvEvent, self._on_communication)

    def send(self, message_inst, src_agent) :
        self._owner.get_event_api().publish(CommunicationSendEvent(src_agent, message_inst, self._network_name))

    def set_recv_callback(self, cb) :
        self._recv_callback = cb

    def get_owner(self) :
        return self._owner

    def set_owner(self, owner) :
        self._owner = owner

    def get_network_name(self) :
        return self._network_name

    def get_name(self) :
        return self._name

    def __getitem__(self, key) :
        if self._attrs.has_key(key) :
            return self._attrs[key]
        return None
