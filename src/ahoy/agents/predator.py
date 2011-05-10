from ahoy.agent import Agent

class PredatorAgent(Agent) :
    def __init__(self, uid) :
        Agent.__init__(self, uid)

    def run(self) :
        while True :
            x, y, z = self.get_owner_node().get_position()
            self.get_owner_node().set_position(x + 1, y + 1, z)
