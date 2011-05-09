from ahoy.event import Event

class DivertEvent(Event) :
    def __init__(self, points) :
        Event.__init__(self)
        self._waypoints = points

    def get_waypoints(self):
        return self._waypoints
