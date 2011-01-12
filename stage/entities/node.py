from stage.entity import Entity

class Node(Entity) :
    def __init__(self, uid) :
        Entity.__init__(self, uid)
        self._interfaces = {}
        self._agents = []

    def add_interface(self, interface) :
        self._interfaces[interface.get_name()] = interface

    def remove_interface(self, name) :
        del self._interface[name]

    def get_interface(self, name) :
        return self._interfaces[name]

    def get_interfaces(self) :
        return self._interfaces.values()

    def add_agent(self, agent_inst) :
        self._agents.append(agent_inst)

    def get_interface_on_net(self, network_name) :
        for iface in self._interfaces.values() :
            if iface.get_network_name() == network_name :
                return iface
        return None

    def run(self) :
        for iface in self._interfaces.values() :
            iface.connect()
        print 'starting node %s' % self._uid
        threads = []
        for a in self._agents :
            threads.append(a.start())
        for t in threads :
            t.join()
