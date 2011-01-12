from stage.events.communication import CommunicationRecvEvent, CommunicationSendEvent

class Interface :
    def __init__(self, name, owner_node, network, power) :
        self._name = name
        self._owner = owner_node
        self._recv_callback = None
        self._network_name = network.get_name()
        self._power = power
        network.add_interface(self)

    def _on_communication(self, event) :
        if event.get_network() == self._network_name :
            if self._owner.get_uid() in event.get_message().get_dests() and self._recv_callback != None :
                self._recv_callback(event, iface=self)

    def connect(self) :
        self._owner.get_event_api().subscribe(CommunicationRecvEvent, self._on_communication)

    def send(self, message_inst) :
        self._owner.get_event_api().publish(CommunicationSendEvent(self.get_owner().get_uid(), self.get_name(), message_inst, self._network_name))

    def set_recv_callback(self, cb) :
        self._recv_callback = cb

    def get_owner(self) :
        return self._owner

    def get_network_name(self) :
        return self._network_name

    def get_name(self) :
        return self._name

    def get_power(self) :
        return self._power
