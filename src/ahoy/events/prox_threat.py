from ahoy.event import Event

# An event which gives a location of a threat and ship being threatened
# by a 'too-close' proximity
class ProximityThreatEvent(Event) :
    def __init__(self, lat, lon, threatened_uid) :
        Event.__init__(self)
        self._threat_lat = lat
        self._threat_lon = lon
        self._threatened_uid = threatened_uid

    def get_threat_location(self) :
        return (self._threat_lat, self._threat_lon) 

    def get_threatened_uid(self) :
        return self._threatened_uid
