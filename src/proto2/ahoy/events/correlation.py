from ahoy.event import Event

# An event with a pair of lat/lons which are correlated
class CorrelationEvent(Event) :
    def __init__(self, point1, point2) :
        Event.__init__(self)
        self._point1 = point1
        self._point2 = point2

    def get_locations(self) :
        return (self._point1, self._point2) 
