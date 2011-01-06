from stage.entity import Entity

class Node(Entity) :
    def __init__(self, uid) :
        Entity.__init__(self, uid)
        self._interfaces = {}

    def add_interface(self, name, interface) :
        self._interfaces[name] = interface

    def remove_interface(self, name) :
        del self._interface[name]
