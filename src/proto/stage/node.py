import sys
from threading import Thread

class Node :
    def __init__(self, model) :
        self._model = Model.from_string(model)

    def start(self) :
        for agent_model in self._model.get('agents') :
            Thread(target=Agent(agent_model)).start()

if __name__ == '__main__' :
    Node(sys.args[1]).start()
