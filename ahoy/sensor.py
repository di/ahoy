class Sensor :
    def __init__(self) :
        self._subscribers = []

    def subscribe(self, callback) :
        self._subscribers.append(callback)

    def _publish_data(self, event) :
        for cb in self._subscribers :
            cb(event)

    def run(self) :
        pass
