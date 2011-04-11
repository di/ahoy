from ahoy.event import Event

class ChemicalSpillEvent(Event) :
    def __init__(self, owner_uid, location, intensity) :
        SensorEvent.__init__(self, owner_uid)
        self._location = location
        self._intensity = intensity

    def get_location(self):
        return self._location

    def get_intensity(self):
        return self._intensity