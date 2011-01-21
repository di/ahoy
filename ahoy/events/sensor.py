from ahoy.event import Event

class SensorEvent(Event) :
    def __init__(self, sensor_id) :
        Event.__init__(self)
        self._uid = sensor_id

    def get_sensor_id(self) :
        return self._uid

class RadarEvent(SensorEvent) :
    def __init__(self, sensor_id, radar_loc, bearing, distance, target_location) :
        SensorEvent.__init__(self, sensor_id)
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
