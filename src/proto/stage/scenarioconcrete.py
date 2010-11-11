from stage.scenario import Scenario
from stage.model import Model

class ScenarioConcrete(Scenario) :
    def __init__(self) :
        Scenario.__init__(self)

        for n in range(0, 10) :
            m = Model(name='n%s' % n, position='1,2', agents = [], interfaces = {})

            for n in range(0, 2) :
                m.get('agents').append(Model(param1='1', param2='2'))

            self._nodes.append(m)
