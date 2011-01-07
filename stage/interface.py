class Interface :
    def __init__(self, owner_node, network) :
        self._owner = owner_node
        self._recv_callback = None
        self._network = network
        self._owner.get_event_api().subscribe(CommunicationRecvEvent, self._on_communication)

    def _on_communication(self, event) :
        if event.get_network().get_name() == self._network.get_name() :
            if owner_node.get_uid() in event.get_dests() and self._recv_callback != None :
                self._recv_callback(event, iface=self)

    def connect(self, network) :
       network.add_interface(self)

    def send(self, message_inst) :
      self._owner.get_event_api().publish(CommunicationSendEvent(message_inst, self._network))

    def set_recv_callback(self, cb) :
        self._recv_callback = cb

    def get_owner(self) :
        return self._owner
