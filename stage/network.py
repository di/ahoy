class Network :
    def __init__(self, name) :
        self._name = name
        self._members = set([])

    def add_interface(self, interface) :
        self._members.add(interface)
