import sys
from threading import Thread
from stage.model import Model
from stage.agent import Agent

class Node :
    def __init__(self, model) :
        self._model = Model.from_string(model)

    def start(self) :
        for agent_model in self._model.get('agents') :
            Agent(agent_model).start()

if __name__ == '__main__' :
    Node(sys.argv[1]).start()
    while True :
        pass
