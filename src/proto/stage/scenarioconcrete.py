from stage.scenario import Scenario
from stage.model import Model

class ScenarioConcrete(Scenario) :
    def __init__(self) :
        Scenario.__init__(self)

        self._nodes = []
        for n in range(0, 1) :
            m = Model(name='n%s' % n, position='1,2', agents = [])

            for n in range(0, 2) :
                m.get('agents').append(Model(param1='1', param2='2'))

            self._nodes.append(m)

    def get_nodes(self) :
        return self._nodes
