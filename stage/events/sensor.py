from stage.event import Event

class SensorEvent(Event) :
    def __init__(self, sensor_id) :
        Event.__init__(self)
        self._uid = sensor_id

    def get_sensor_id(self) :
        return self._uid

class RadarEvent(SensorEvent) :
    def __init__(self, sensor_id, data) :
        SensorEvent.__init__(self, sensor_id)
        self._data = data

    def get_data(self) :
        return self._data
