from ahoy.event import Event

class LinkEvent(Event) :
    def __init__(self, up, uid_1, uid_2, network_name, pathloss=None) :
        Event.__init__(self)
        self._up = up
        self._uid_1 = uid_1
        self._uid_2 = uid_2
        self._network_name = network_name
        self._pathloss = pathloss

    def get_up(self) :
        return self._up

    def get_uid1(self) :
        return self._uid_1

    def get_uid2(self) :
        return self._uid_2

    def get_network_name(self) :
        return self._network_name

    def get_pathloss(self) :
        return self._pathloss
