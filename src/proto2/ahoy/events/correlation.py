from ahoy.event import Event

# An event with a pair of lat/lons which are correlated
class CorrelationEvent(Event) :
    def __init__(self, point1_lat, point1_lon, point2_lat, point2_lon) :
        Event.__init__(self)
        self._point1 = (point1_lat, point1_lon)
        self._point2 = (point2_lat, point2_lon)

    def get_locations(self) :
        return (self._point1, self._point2) 
