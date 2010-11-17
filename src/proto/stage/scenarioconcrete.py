from stage.scenario import Scenario
from stage.model import Model
from stage.agents.testagent import TestAgent
from stage.agents.randommoveagent import MovingAgent

class ScenarioConcrete(Scenario) :
    def __init__(self) :
        Scenario.__init__(self)

        m = Model(name='n0', position=(0,0,0), agents = [], interfaces = {})
        m.get('agents').append(MovingAgent(Model(job='send')))
        n = Model(name='n1', position=(15,15,0), agents = [], interfaces = {})
        n.get('agents').append(MovingAgent(Model(job='send')))
        self._nodes.append(m)
        self._nodes.append(n)

