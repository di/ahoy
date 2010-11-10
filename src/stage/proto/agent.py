from threading import Thread

class Agent(Thread) :
    def __init__(self, model) :
        self._model = Model.from_string(model)

    def run(self) :
        pass
