class Sensor :
    def __init__(self, owner_uid) :
        self._owner_uid = owner_uid
        self._world = None
        self._subscribers = []

    def get_owner_uid(self) :
        return self._owner_uid

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
