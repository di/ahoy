from stage.entity import Entity

class Node(Entity) :
    def __init__(self, uid) :
        Entity.__init__(self, uid)
        self._interfaces = {}
        self._agents = []

    def add_interface(self, name, interface) :
        self._interfaces[name] = interface

    def remove_interface(self, name) :
        del self._interface[name]

    def get_interface(self, name) :
        return self._interfaces[name]

    def get_interfaces(self) :
        return self._interfaces.values()

    def add_agent(self, agent_inst) :
        self._agents.append(agent_inst)

    def run(self) :
        for iface in self._interfaces.values() :
            iface.connect()
        print 'starting node %s' % self._uid
        threads = []
        for a in self._agents :
            threads.append(a.start())
        for t in threads :
            t.join()
