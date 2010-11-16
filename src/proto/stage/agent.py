from threading import Thread
from stage.api import API

class Agent :
    def __init__(self, model) :
        self._model = model

    def set_owner(self, node) :
        self._owner = node
        self._api = API(node)

    def run(self) :
        pass
