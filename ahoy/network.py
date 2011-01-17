class Network :
    def __init__(self, name) :
        self._name = name
        self._interfaces = set([])
        self._link_cache = {}

    def get_name(self) :
        return self._name

    def add_interface(self, interface) :
        self._interfaces.add(interface)

    def check_cache(self, node1_uid, node2_uid, pathloss=None) :
        if not self._link_cache.has_key((node1_uid, node2_uid)) or self._link_cache[(node1_uid, node2_uid)] != pathloss :
            # This is kind of a hack, but it's simpler than creating an
            # object and writing a cmp function...
            self._link_cache[(node1_uid, node2_uid)] = pathloss
            self._link_cache[(node2_uid, node1_uid)] = pathloss
            return True
        else :
            return False

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
