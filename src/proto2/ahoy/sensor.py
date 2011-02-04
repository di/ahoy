class Sensor :
    def __init__(self) :
        self._owner = None
        self._world = None
        self._subscribers = []

    def get_owner(self) :
        return self._owner

    def set_owner(self, owner) :
        self._owner = owner

    def subscribe(self, callback) :
        self._subscribers.append(callback)

    def _publish_data(self, event) :
        for cb in self._subscribers :
            cb(event)

    def get_world(self) :
        return self._world

    def _run(self, world) :
        self._world = world
        self.run()

    def run(self) :
        pass
