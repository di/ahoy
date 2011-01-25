from ahoy.events.communication import CommunicationRecvEvent, CommunicationSendEvent

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
            agents = set(event.get_message().get_dest_agents())
            local_agents = set(self.get_owner().get_agent_uids())
            if not agents.isdisjoint(local_agents) and self._recv_callback != None :
                self._recv_callback(event, iface=self)

    def connect(self) :
        self._owner.get_event_api().subscribe(CommunicationRecvEvent, self._on_communication)

    def send(self, message_inst, src_agent) :
        self._owner.get_event_api().publish(CommunicationSendEvent(src_agent, self.get_name(), message_inst, self._network_name))

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
