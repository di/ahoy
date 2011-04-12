from ahoy.event import Event

class ChemicalSpillEvent(Event) :
    def __init__(self, location, rate) :
        Event.__init__(self)
        self._location = location
        self._rate = rate       # rate is in km per seconds

    def get_location(self):
        return self._location

##    def get_intensity(self):
##        return self._intensity

    # rate is in km per seconds
    def get_rate(self):
        return self._rate
