from events import *

class Event :
    def __init__(self, event_model) :
        self._model = event_model

    def __str__(self) :
        return self._model.__str__()
