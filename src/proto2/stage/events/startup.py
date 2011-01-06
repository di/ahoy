from stage.event import Event

class StartupEvent(Event) :
    def __init__(self, world) :
        Event.__init__(self)
        self._world = world

    def get_world(self) :
        return self._world

class AckStartupEvent(Event) :
    def __init__(self, daemon_id) :
        Event.__init__(self)
        self._daemon_id = daemon_id

    def get_daemon_id(self) :
        return self._daemon_id

class StartSimulationEvent(Event) :
    def __init__(self) :
        Event.__init__(self)
