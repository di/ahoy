from stage.scenario import Scenario
from stage.model import Model
from stage.agents.testagent import TestAgent

class ScenarioConcrete(Scenario) :
    def __init__(self) :
        Scenario.__init__(self)

        for n in range(0, 4) :
            m = Model(name='n%s' % n, position=(0,0,0), agents = [], interfaces = {})

            if n % 2 == 0 :
                m.get('agents').append(TestAgent(Model(job='send')))
            else :
                m.get('agents').append(TestAgent(Model(job='recv')))

            self._nodes.append(m)
