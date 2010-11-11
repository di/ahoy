from threading import Thread
from stage.api import API

class Agent :#(Thread) :
    def __init__(self, model) :
        #Thread.__init__(self)
        self._model = model

    def set_owner(self, node) :
        self._owner = node
        self._api = API(node.get_name())

    def run(self) :
        pass
