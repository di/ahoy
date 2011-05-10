from ahoy.event import Event

class PredatorMessage(Event) :
    def __init__(self, contents) :
        self._contents = contents

    def get_contents(self) :
        return self._contents
