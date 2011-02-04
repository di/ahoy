from ahoy.event import Event

class RadarEvent(Event) :
    def __init__(self, radar_loc, bearing, distance, target_location) :
        Event.__init__(self)
        self._radar_loc = radar_loc
        self._bearing = bearing
        self._distance = distance
        self._target_location = target_location

    def get_radar_loc(self) :
        return self._radar_loc

    def get_bearing(self) :
        return self._bearing

    def get_distance(self) :
        return self._distance

    def get_target_location(self) :
        return self._target_location
