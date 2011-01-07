from stage.event import Event

class EntityMoveEvent(Event) :
    def __init__(self, lat, long, agl) :
        Event.__init__(self)
        self._lat = lat
        self._long = long
        self._agl = agl

    def get_lat(self) :
        return self._lat

    def get_long(self) :
        return self._long

    def get_agl(self) :
        return self._agl
