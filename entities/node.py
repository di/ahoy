from ahoy.entity import Entity

class Node(Entity) :
    def __init__(self, uid) :
        Entity.__init__(self, uid)
        self._interfaces = {}
        self._agents = {}
        self._routing_agent = None

    def set_routing_agent(self, agent) :
        self._routing_agent = agent

    def get_routing_agent(self) :
        return self._routing_agent

    def get_agent_uids(self) :
        return self._agents.keys()

    def add_interface(self, interface) :
        self._interfaces[interface.get_name()] = interface
        interface.set_owner(self)

    def remove_interface(self, name) :
        del self._interface[name]

    def get_interface(self, name) :
        return self._interfaces[name]

    def get_interfaces(self) :
        return self._interfaces.values()

    def add_agent(self, agent_inst) :
        self._agents[agent_inst.get_uid()] = agent_inst
        agent_inst.set_owner_node(self)

    def get_interface_on_net(self, network_name) :
        for iface in self._interfaces.values() :
            if iface.get_network_name() == network_name :
                return iface
        return None

    def send(self, message, src_agent, iface=None) :
        assert not (message.get_dest_agent() == '*' and iface == None)
        if iface == None :
            for iface in self._interfaces.values() :
                network = self.get_world().get_network(iface.get_network_name())

                node_uid = self.get_world().get_agent_mapping()[message.get_dest_agent()]
                if network.both_in_network(self.get_uid(), node_uid) :
                    iface.send(message, src_agent.get_uid())
                    break
        else :
            iface.send(message, src_agent.get_uid())

    def _on_message(self, event, **kwds) :
        self._agents[event.get_message().get_dest_agent()].on_message(event)

    def run(self) :
        print 'starting node %s' % self._uid

        for iface in self._interfaces.values() :
            iface.connect()
            iface.set_recv_callback(self._on_message)
        
        lat, lon, agl = self.get_position()
        self.set_position(lat, lon, agl)

        threads = []
        for a in self._agents.values() :
            threads.append(a.start())
        for t in threads :
            t.join()
