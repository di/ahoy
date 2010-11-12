import sys
from threading import Thread
from stage.model import Model
from stage.agent import Agent

class Node :
    def __init__(self, model) :
        self._model = Model.from_string(model)
        self._name = self._model.get('name')

    def get_name(self) :
        return self._name

    def get_model(self) :
        return self._model

    def start(self) :
        for agent_model in self._model.get('agents') :
            agent_model.set_owner(self)
            Thread(target=agent_model.run()).start()#Agent(agent_model, self).start()

if __name__ == '__main__' :
    Node(sys.argv[1]).start()
    while True :
        pass
