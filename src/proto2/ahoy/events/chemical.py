from ahoy.event import Event

class ChemicalSpillEvent(Event) :
    def __init__(self, location, intensity) :
        Event.__init__(self)
        self._location = location
        self._intensity = intensity

    def get_location(self):
        return self._location

    def get_intensity(self):
        return self._intensity