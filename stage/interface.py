class Interface :
    def __init__(self, owner_node) :
        self._owner = owner_node

    def connect(self, network) :
       network.add_interface(self)

    def get_owner(self) :
        return self._owner
