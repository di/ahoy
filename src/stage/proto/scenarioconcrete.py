class ScenarioConcrete(Scenario) :
    def __init__(self) :
        Scenario.__init__(self)

        self._nodes = []
        for n in range(0, 5) :
            m = Model(name='n' + n, 'position'='1,2', 'agents' = [])

            for n in range(0, 2) :
                m.get('agents').append(Model('param1'='1', 'param2'='2'))

            self._nodes.append(m)

    def get_nodes(self) :
        return self._nodes
