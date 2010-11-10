from threading import Thread

class Agent(Thread) :
    def __init__(self, model) :
        Thread.__init__(self)
        self._model = model

    def run(self) :
        pass
