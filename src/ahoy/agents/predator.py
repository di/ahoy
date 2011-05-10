from ahoy.agent import Agent

class PredatorAgent(Agent) :
    def __init__(self, uid) :
        Agent.__init__(self, uid)

    def run(self) :
        dist = 1/50.0
        while True :
            y, x, z = self.get_owner_node().get_position()
            print x, y, z
            self.get_owner_node().move(y + dist, x + dist, 0, dist / 5, 0, True)
