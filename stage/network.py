class Network :
    def __init__(self, name) :
        self._name = name
        self._interfaces = set([])

    def get_name(self) :
        return self._name

    def add_interface(self, interface) :
        self._interfaces.add(interface)

    #TODO: This method is terrible...
    def both_in_network(self, node1_uid, node2_uid) :
        n1 = False
        n2 = False
        for iface in self._interfaces :
            if iface.get_owner().get_uid() == node1_uid :
                n1 = True
            if iface.get_owner().get_uid() == node2_uid :
                n2 = True
            if n1 and n2 :
                return True
        return False
