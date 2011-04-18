from ahoy.event import Event

class SensorEvent(Event) :
    def __init__(self, owner_uid) :
        Event.__init__(self)
        self._owner_uid = owner_uid

    def get_owner_uid(self) :
        return self._owner_uid

    def __str__(self) :
        return 'Not yet implemented'
