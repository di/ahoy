from stage.event import Event

class MoveReqEvent(Event) :
    def __init__(self, lat, long) :
        self._lat = lat
        self._long = long

    def get_lat(self) :
        return self._lat

    def get_long(self) :
        return self._long
